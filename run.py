#!/usr/bin/env python

import argparse
import time
import glob
import os
import subprocess

try:
    import jpype
except ImportError:
    print 'Warning: Could not import jpype, Test server wont be available'
    jpype = None
from flask_debugtoolbar import DebugToolbarExtension

import ui
import model
import db


def start_memory_db(args):
    if not jpype:
        print 'Error: JPype could not be imported, test server can not be startet'
        return

    if not os.path.isdir(args.neo4j_path):
        raise Exception('--neo4j_path %r is no directory' % args.neo4j_path)

    dir1 = os.path.join(args.neo4j_path, 'system', 'lib')
    dir2 = os.path.join(args.neo4j_path, 'lib')

    # The file neo4j-kernel-*-tests.jar must be download and added to
    # lib or system/lib manually
    if not (glob.glob(os.path.join(dir1, 'neo4j-kernel-*-tests.jar')) or
            glob.glob(os.path.join(dir2, 'neo4j-kernel-*-tests.jar'))):
        raise Exception('Jar file neo4j-kernel-*-tests.jar was not found in lib or system/lib')

    jars = glob.glob(os.path.join(dir1, '*.jar')) + glob.glob(os.path.join(dir2, '*.jar'))


    jvm_args = '-Djava.class.path=%s' % ':'.join(jars)
    jpype.startJVM("/usr/lib/jvm/java-6-openjdk/jre/lib/amd64/server/libjvm.so", jvm_args)


    ImpermanentGraphDatabase = getattr(jpype.JPackage('org.neo4j.test'), 'ImpermanentGraphDatabase')
    WrappingNeoServerBootstrapper = getattr(jpype.JPackage('org.neo4j.server'), 'WrappingNeoServerBootstrapper')
    ServerConfigurator = getattr(jpype.JPackage('org.neo4j.server.configuration'), 'ServerConfigurator')

    db = ImpermanentGraphDatabase()
    config = ServerConfigurator(db)
    config.configuration().setProperty(ServerConfigurator.WEBSERVER_PORT_PROPERTY_KEY, 7475)
    server = WrappingNeoServerBootstrapper(db, config)
    server.start()

    while True:
        # Testserver will stop if the python process exits, so loop forever
        time.sleep(1000)


def start_neo4j(args):
    path = os.path.join(args.neo4j_path, 'bin', 'neo4j')
    subprocess.call([path, 'start'])


def stop_neo4j(args):
    path = os.path.join(args.neo4j_path, 'bin', 'neo4j')
    subprocess.call([path, 'stop'])


def export_xml(args):
    outf = open('export.graphml', 'w')
    outf.write(g.get_graphml())


def start_ui(args):
    model.init_relationship_classes()
    model.init_graph(model.g)
    ui.app.debug = True
    ui.app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    ui.app.secret_key = 'Todo'
    if True:
        toolbar = DebugToolbarExtension(ui.app)
    ui.app.run(host='0.0.0.0', port=5001)


def reset_db(args):
    if not args.force:
        answer = raw_input('Really import data (y,N)? ')
        if answer != 'y':
            print 'Abort'
            return

    #model.init_node_classes()
    model.init_relationship_classes()
    model.init_graph(model.g)
    model.g.clear()
    #g = db.init_graph() # must initialize a second time after clear, dont know why
    db.reset_db(args.csv_path)


COMMANDS = {
    'memory_db': start_memory_db,
    'ui': start_ui,
    'export_xml': export_xml,
    'reset_db': reset_db,
    'neo4jstart': start_neo4j,
    'neo4jstop': stop_neo4j,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('command', choices=COMMANDS.keys(), help='Run one of the commands')
    parser.add_argument('--neo4j_path', default='neo4j-community-1.8.1', help='Path to the neo4j directory')
    parser.add_argument('--force', action="store_true", help='Force yes on user input for the given command')
    parser.add_argument('--csv_path', default='/home/ben/projects/wikipedia-csv/csv/all.csv', help='Path to csv files')

    args = parser.parse_args()

    COMMANDS[args.command](args)
