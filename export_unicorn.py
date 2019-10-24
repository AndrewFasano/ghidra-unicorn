# Export a pickle that can be injested by unicorn

#@author Andrew Fasano
#@category Emulation
#@keybinding 
#@menupath Tools.UnicornExport
#@toolbar 

import pickle
import jarray

output = {"mem_regions": [], # (start,size) tuples
          "data": {}}  # address: data

# Chop program into 4K aligned memory regions for unicorn
def get_address_ranges(program, blocks):
    address_ranges = []

    for block in blocks:
        if block.getStart().addressSpace .name != u'ram':
            continue
        (s,e) = (int(block.getStart().offset) & ~0x4000, int(block.getEnd().offset) | 0x3FFF) # round to 0x4k boundries
        #print(hex(s) + " - " + hex(e))

        assert(s < e), "Can't have start < end"
        (start_overlaps, end_overlaps) = (None, None)
        for (start, end) in address_ranges:
            if s >= start and e <= end:
                break
            elif s >= start and s <= end: # Start overlaps with existing range - extend
                start_overlaps = (start, end)
                break
            elif e >= start and e <= end: # End overlaps with existing range - extend
                end_overlaps = (start, end)
                break
        else: # No overlaps or existing data - insert
            address_ranges.append((s, e))
            continue

        assert(not(start_overlaps and end_overlaps))
        if start_overlaps: # Expand existing range to have new end
            address_ranges[:] = [(x,y) for (x,y) in address_ranges if (x,y) != start_overlaps]
            address_ranges.append((start_overlaps[0], e))

        elif end_overlaps: # Move start of existing range to be earlier
            address_ranges[:] = [(x,y) for (x,y) in address_ranges if (x,y) != end_overlaps]
            address_ranges.append((s, end_overlaps[1]))

    #print("ADDRESS RANGES:")
    #for (s, e) in address_ranges:
    #    print(hex(s) + " - " + hex(e))

    return address_ranges

blocks = currentProgram.getMemory().getBlocks()
ranges = get_address_ranges(currentProgram, blocks)

# Map memory (TODO: also store memory permissions)
for (start,end) in ranges:
    output["mem_regions"].append((start, end-start+1))
    assert(end-start >0)

# Set up data
for block in blocks:
    if block.getStart().addressSpace .name != u'ram': # Only copy ram (TODO: should we copy other regions?)
        continue
    l = block.size
    if block.isInitialized(): # Only read initialized blocks
        java_bytes = jarray.zeros(l, "b")
        len_bytes = block.getBytes(block.start, java_bytes)
        block_bytes = bytearray([int((b+2**32)&0xff)  for b in java_bytes[:len_bytes]])

        mapped = False
        for (s,e) in ranges:
            if block.start.offset >= s and block.start.offset <= e:
                break
        else:
            raise RuntimeError("Block at 0x{:x} is unmapped".format(block.start.offset))

        # Now write from start to end
        output["data"][int(block.start.offset)] = block_bytes
        print("Wrote {} bytes at {:x}".format(len(block_bytes), int(block.start.offset)))
    #else:
    #    print("Ignore Uninitialized block at ", block.start)


out = askDirectory("Save location", "Save")
d = out.toString().encode("utf8")
with open(d, "wb") as f:
    pickle.dump(output, f)
