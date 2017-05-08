# -*- coding: utf-8 -*-
"""
    Blockstack-tor
    ~~~~~
    copyright: (c) 2014-2015 by Halfmoon Labs, Inc.
    copyright: (c) 2016-2017 by Blockstack.org

    This file is part of Blockstack-tor.

    Blockstack-tor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Blockstack-tor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Blockstack-tor.  If not, see <http://www.gnu.org/licenses/>.
"""

import stem
import stem.control

import os
import pwd
import re
import atexit
import time
import sys
import threading
import getopt 

import blockstack_client

from .version import __version__

DEBUG = blockstack_client.constants.BLOCKSTACK_DEBUG

log = blockstack_client.get_logger('blockstack-tor')

TOR_CONTROL_PORT = 9051
BLOCKSTACK_TLDS = ['.id']       # TLDs we intercept


class BlockstackOnionResolver(threading.Thread):
    """
    Class to take a name that ends in a supported TLD
    and convert it into the appropriate .onion address.
    """
    def __init__(self, controller, stream, addr):
        threading.Thread.__init__(self)
        self.addr = addr
        self.stream = stream
        self.controller = controller


    def run(self):
        """
        Carry out the name resolution
        """
        onion_addr = blockstack_tor_resolve(self.addr)
        if not onion_addr:
            # force failure
            onion_addr = "unknown"

        # redirect the stream and attach it to Tor
        res = self.controller.msg('REDIRECTSTREAM {} {}'.format(self.stream.id, onion_addr))
        if not res.is_ok():
            log.error("Failed to 'REDIRECTSTREAM'\nRaw error:\n{}".format(res.raw_content()))

        else:
            log.debug("Resolved {} to {}".format(self.addr, onion_addr))

        # attach the stream to Tor
        attach_stream_to_tor(self.controller, self.stream)
        return
       


def blockstack_tor_resolve( name ):
    """
    Given the name (a blockchain ID), resolve it to a .onion address.
    The blockchain ID's zone file must have a TXT record called 'tor',
    and its text data should be a .onion address.  There should be exactly
    one 'tor' name.

    Return the .onion address on success.
    Return None on error
    """

    if name == 'duckduckgo_tor.id':
        return '3g2upl4pq6kufc4m.onion'

    # fetch and parse zone file...
    try:
        zonefile_data = blockstack_client.get_name_zonefile(name)
    except Exception as e:
        if DEBUG:
            log.exception(e)

        return None

    if 'error' in zonefile_data:
        log.error("Failed to look up {}: {}".format(name, zonefile_data['error']))
        return None

    # is there a TXT record called 'tor'?
    zonefile = zonefile_data['zonefile']
    txt_recs = zonefile.get('txt', [])
    tor_txt_recs = filter(lambda txtrec: txtrec.get('name') == 'tor', txt_recs)

    if len(tor_txt_recs) == 0:
        log.error("No 'tor' TXT records for {}".format(name))
        return None

    if len(tor_txt_recs) > 1:
        log.error("Multiple 'tor' TXT records for {}".format(name))
        return None

    tor_txt_rec = tor_txt_recs[0]

    # get the .onion address, and verify that it's well-formed
    onion_addr_str = tor_txt_rec.get('txt', None)
    if onion_addr_str is None:
        log.error("No text in tor TXT record for {}".format(name))
        return None

    if not re.match('^[0-9A-V=]{16}\.onion$', onion_addr_str):
        log.error("Invalid tor TXT record for {}".format(name))
        return None

    # resolved!
    return onion_addr_str


def attach_stream_to_tor( controller, stream ):
    """
    Given a stream, attach it back to Tor.

    Return True on success
    Raise on error
    """
    try:
        controller.attach_stream(stream.id, 0)
    except stem.UnsatisfiableRequest:
        pass
    except stem.InvalidRequest as ire:
        log.warning("Invalid request (code {})".format(ire.code))
        pass

    return True


def delegate_name_resolution( controller, stream ):
    """
    When we get a STREAM event, fire up a thread to
    asynchronously redirect the stream by rewriting
    its target address if the target address is 
    a Blockstack name.
    """
    target_addr = stream.target_address
    for tld in BLOCKSTACK_TLDS:
        if target_addr.endswith(tld):
            # we can handle this!
            log.debug("Try to handle {}".format(target_addr))
            t = BlockstackOnionResolver(controller, stream, target_addr)
            t.start()
            return
            
    # can't handle this, but make sure
    # this stream gets attached to a circuit
    # by Tor
    if stream.circ_id is None:
        # no circuit set yet.
        # let Tor do it.
        attach_stream_to_tor(controller, stream)

    return


def connect_tor(password=None, port=None):
    """
    Connect to Tor's control port, authenticate,
    and begin intercepting STREAM events from Tor.

    Returns the Tor controller instance on success.
    Raises on error.
    """

    log.debug("Connect to Tor on port {}".format(port))
    
    controller = stem.control.Controller.from_port(port=port)

    try:
        # connect to Tor with a cookie
        controller.authenticate()
    except stem.connection.MissingPassword:
        # try with given password 
        if password is None:
            password = raw_input("Enter Tor controller password: ")

        controller.authenticate(password=password)

    # we will explicitly attach streams to circuits, once we've
    # added ourselves on to the stream.
    controller.set_options( {'__LeaveStreamsUnattached': '1'} )

    # start rewriting stream addresses
    controller.add_event_listener( lambda stream: delegate_name_resolution(controller, stream), stem.control.EventType.STREAM )

    return controller


def atexit_shutdown(controller):
    """
    Try to be nice and close the connection 
    on exit.
    """
    try:
        controller.close()
    except:
        pass


def main(argv):
    """
    Proceed to resolve names forever.
    argv:
        * -p/--password <tor controller password>
        * -P/--port <tor controller port>
        * -H/--blockstack-hostport <blockstack host:port>
    """

    opts_list, prog_args = getopt.getopt(sys.argv[1:], 'p:P:H:',  ['password=', 'port=', 'blockstack-node='])

    password = None
    port = TOR_CONTROL_PORT
    blockstack_hostport = None

    for (argname, argval) in opts_list:
        if argname == '-p' or argname == '--password':
            password = argval

        if argname == '-P' or argname == '--port':
            port = int(argval)

        if argname == '-H' or argname == '--blockstack-node':
            blockstack_hostport = argval

    if blockstack_hostport:
        blockstack_host, blockstack_port = blockstack_client.utils.url_to_host_port(blockstack_hostport)
        if blockstack_host is None or blockstack_port is None:
            print >> sys.stderr, "Invalid argument: {}".format(blockstack_hostport)
            sys.exit(1)

    blockstack_client.session(server_host=blockstack_host, server_port=blockstack_port, set_global=True)
    controller = connect_tor(password=password, port=port)
    atexit.register(atexit_shutdown, controller)
    
    while True:
        try:
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
 
