#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import argparse

# TODO: make actual arguments - currently set for PLA and 5mm differences
def main(data, start_temp=225.0, temp_inc=5.0, height_inc=5.0):
    # Set our command regex
    cmd_re = re.compile((
        r'G[0-9]+\.?[0-9]* F[0-9]+\.?[0-9]* X[0-9]+\.?[0-9]* '
        r'Y[0-9]+\.?[0-9]* Z([0-9]+\.?[0-9]*)'
    ))

    # Set initial state
    output = []
    current_temp = start_temp
    started = False
    z = 0.0
    new_temp = 0

    for layer in data.splitlines():
        output_line = ''
        for line in layer.split('\n'):
            # If we see LAYER:0, this means we are in the main layer code
            if 'LAYER:0' in line:
                print("LAYER:0 found")
                started = True

            # output any comment lines or pre-start lines
            # without modification
            if line.startswith(';') or not started:
                output_line += '%s\n' % line
                continue

            # Find the X,Y,Z Line (ex. G0 X60.989 Y60.989 Z1.77)
            match = cmd_re.search(line)

            # If we've found our line
            if match is not None:
                # Grab the z value
                new_z = float(match.groups()[0])

                # If our z value has changed
                if new_z != z:
                    z = new_z

                    # Determine new temperature
                    new_temp = int(z / height_inc) * temp_inc
                    new_temp = start_temp - new_temp

                    # If we hit a spot where we need to change the
                    # temperature, then write the gcode command
                    if new_temp < current_temp:
                        print("Adding new temp %f") % (new_temp)
                        current_temp = new_temp
                        output_line += ';TYPE:CUSTOM\n'
                        output_line += 'M104 S%d\n' % new_temp
            # output the current line
            output_line += '%s\n' % line
        # Append the current possibly modified layer to the output
        output.append(output_line)
    return output

if __name__ == "__main__":
    
    if len(sys.argv) < 1:
        sys.exit(-1)
    
    with open(sys.argv[1], 'rb') as f:
        gcode_data = f.read()

    print("Read: %d from %s") % (len(gcode_data), sys.argv[1])
    
    output = main(gcode_data)

    print("Result: %d into %s") % (len(output), sys.argv[1]+".mod.gcode")
    with open(sys.argv[1]+".mod.gcode", "wb") as f:
        f.writelines(output)
    




    