import pycstruct, sounddevice, numpy
import matplotlib.pyplot as plt

# WAV file header
header_def = pycstruct.StructDef(default_byteorder = 'little')
header_def.add('utf-8', 'ChunkID', length=4)
header_def.add('uint32', 'ChunkSize')
header_def.add('utf-8', 'Format', length=4)
header_def.add('utf-8', 'Subchunk1ID', length=4)
header_def.add('uint32', 'Subchunk1Size')
header_def.add('uint16', 'AudioFormat')
header_def.add('uint16', 'NumChannels')
header_def.add('uint32', 'SampleRate')
header_def.add('uint32', 'ByteRate')
header_def.add('uint16', 'BlockAlign')
header_def.add('uint16', 'BitsPerSample')
header_def.add('utf-8', 'Subchunk2ID', length=4)
header_def.add('uint32', 'Subchunk2Size')


with open('48KHz_8KHz_48KHz_Sample_48KHz_Mono.wav', 'rb') as f:
    # Read header to figure out data size and length
    header_bytes = f.read(header_def.size())
    header = header_def.deserialize(header_bytes)
    print(header)

    # Read the data
    data_def = pycstruct.StructDef(default_byteorder = 'little')
    nbr_elements = int(8 * header['Subchunk2Size'] / header['BitsPerSample'])
    data_def.add('uint' + str(header['BitsPerSample']), 'data', length=nbr_elements)
    data_bytes = f.read()
    data = data_def.deserialize(data_bytes)
    print(len(data['data']))

# Play sound
sound = numpy.array(data['data'], dtype=numpy.uint8)
sounddevice.play(sound, samplerate=header['SampleRate'])

# Plot audio signal
plt.title('48KHz_8KHz_48KHz_Sample_48KHz_Mono.wav')
plt.plot(sound)
plt.show()






