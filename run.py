#!/usr/bin/env python

import argparse
import time
import glob
import os



try:
    import jpype
except ImportError:
    print 'Warning: Could not import jpype, Test server wont be available'
    jpype = None
    

def start_test_server(args):
    if not jpype:
        print 'Error: JPype could not be imported, test server can not be startet'
        return

    glob1 = os.path.join(args.neo4j_path, 'system', 'lib', '*.jar')
    glob2 = os.path.join(args.neo4j_path, 'lib', '*.jar')

    jars = glob.glob(glob1) + glob.glob(glob2)

    jvm_args = '-Djava.class.path=%s' % ':'.join(jars)
    jpype.startJVM("/usr/lib/jvm/java-6-openjdk/jre/lib/amd64/server/libjvm.so", jvm_args)


    ImpermanentGraphDatabase = getattr(jpype.JPackage('org.neo4j.test'), 'ImpermanentGraphDatabase')
    WrappingNeoServerBootstrapper = getattr(jpype.JPackage('org.neo4j.server'), 'WrappingNeoServerBootstrapper')

    db = ImpermanentGraphDatabase()
    server = WrappingNeoServerBootstrapper(db)
    server.start()

    while True:
        # Testserver will stop if the python process exits, so loop forever
        time.sleep(1000)


COMMANDS = {
    'test_server': start_test_server,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('command', choices=COMMANDS.keys(), help='Run one of the commands')
    parser.add_argument('--neo4j_path', default='neo4j-community-1.8.1', help='Path to the neo4j directory')
    
    args = parser.parse_args()

    COMMANDS[args.command](args)
