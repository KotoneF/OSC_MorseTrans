import pyaudio
import numpy as np
import math
import time
import asyncio

from pythonosc import udp_client

client = udp_client.SimpleUDPClient('127.0.0.1', 9000)

samplerate = 4096
fs = 20
index = 2
threshold = -40

dot_length = 8

char_digit = 1

charqueue = []

isWabun = False

morsecode = {
    '.-': 'A',
    '-...': 'B',
    '-.-.': 'C',
    '-..': 'D',
    '.': 'E',
    '..-.': 'F',
    '--.': 'G',
    '....': 'H',
    '..': 'I',
    '.---': 'J',
    '-.-': 'K',
    '.-..': 'L',
    '--': 'M',
    '-.': 'N',
    '---': 'O',
    '.--.': 'P',
    '--.-': 'Q',
    '.-.': 'R',
    '...': 'S',
    '-': 'T',
    '..-': 'U',
    '...-': 'V',
    '.--': 'W',
    '-..-': 'X',
    '-.--': 'Y',
    '--..': 'Z',
    '.----': '1',
    '..---': '2',
    '...--': '3',
    '....-': '4',
    '.....': '5',
    '-....': '6',
    '--...': '7',
    '---..': '8',
    '----.': '9',
    '-----': '0',
    '..--..': '?',
    '-....-': '-',
    '.-.-.': '+',
    '-...-': '=',
    '.-.-.': 'AR',
    '.-...': 'AS',
    '...-.-': 'VA',
    '-.--.': 'KN',
    '...---...': 'SOS',
    '-..---': 'ﾎﾚ'
}

wabuncode = {
    '.-': 'ｲ',
    '.-.-': 'ﾛ',
    '-...': 'ﾊ',
    '-.-.': 'ﾆ',
    '-..': 'ﾎ',
    '.': 'ﾍ',
    '..-..': 'ﾄ',
    '..-.': 'ﾁ',
    '--.': 'ﾘ',
    '....': 'ﾇ',
    '-.--.': 'ﾙ',
    '.---': 'ｦ',
    '-.-': 'ﾜ',
    '.-..': 'ｶ',
    '--': 'ﾖ',
    '-.': 'ﾀ',
    '---': 'ﾚ',
    '---.': 'ｿ',
    '.--.': 'ﾂ',
    '--.-': 'ﾈ',
    '.-.': 'ﾅ',
    '...': 'ﾗ',
    '-': 'ﾑ',
    '..-': 'ｳ',
    '.-..-': 'ｲ',
    '..--': 'ﾉ',
    '.-...': 'ｵ',
    '...-': 'ｸ',
    '.--': 'ﾔ',
    '-..-': 'ﾏ',
    '-.--': 'ｹ',
    '--..': 'ﾌ',
    '----': 'ｺ',
    '-.---': 'ｴ',
    '.-.--': 'ﾃ',
    '--.--': 'ｱ',
    '-.-.-': 'ｻ',
    '-.-..': 'ｷ',
    '-..--': 'ﾕ',
    '-...-': 'ﾒ',
    '..-.-': 'ﾐ',
    '--.-.': 'ｼ',
    '.--..': 'ｴ',
    '--..-': 'ﾋ',
    '-..-.': 'ﾓ',
    '.---.': 'ｾ',
    '---.-': 'ｽ',
    '.-.-.': 'ﾝ',
    '..': '゛',
    '..--.': '゜',
    '...-.': 'ﾗﾀ',
    '.----': '1',
    '..---': '2',
    '...--': '3',
    '....-': '4',
    '.....': '5',
    '-....': '6',
    '--...': '7',
    '---..': '8',
    '----.': '9',
    '-----': '0',
    '.--.-': '-',
    '........': 'HH',
}

osc_chars = {
    ' ': 0,
    'A': 1,
    'B': 2,
    'C': 3,
    'D': 4,
    'E': 5,
    'F': 6,
    'G': 7,
    'H': 8,
    'I': 9,
    'J': 10,
    'K': 11,
    'L': 12,
    'M': 13,
    'N': 14,
    'O': 15,
    'P': 16,
    'Q': 17,
    'R': 18,
    'S': 19,
    'T': 20,
    'U': 21,
    'V': 22,
    'W': 23,
    'X': 24,
    'Y': 25,
    'Z': 26,
    '!': 27,
    '?': 28,
    '1': 30,
    '2': 31,
    '3': 32,
    '4': 33,
    '5': 34,
    '6': 35,
    '7': 36,
    '8': 37,
    '9': 38,
    '0': 39,
    '=': 40,
    '-': 41,
    '+': 42,
    'ｱ': 45,
    'ｲ': 46,
    'ｳ': 47,
    'ｴ': 48,
    'ｵ': 49,
    'ｶ': 50,
    'ｷ': 51,
    'ｸ': 52,
    'ｹ': 53,
    'ｺ': 54,
    'ｻ': 60,
    'ｼ': 61,
    'ｽ': 62,
    'ｾ': 63,
    'ｿ': 64,
    'ﾀ': 65,
    'ﾁ': 66,
    'ﾂ': 67,
    'ﾃ': 68,
    'ﾄ': 69,
    'ﾅ': 75,
    'ﾆ': 76,
    'ﾇ': 77,
    'ﾈ': 78,
    'ﾉ': 79,
    'ﾊ': 80,
    'ﾋ': 81,
    'ﾌ': 82,
    'ﾍ': 83,
    'ﾎ': 84,
    'ﾏ': 90,
    'ﾐ': 91,
    'ﾑ': 92,
    'ﾒ': 93,
    'ﾓ': 94,
    'ﾔ': 95,
    'ﾕ': 96,
    'ﾖ': 97,
    'ﾗ': 105,
    'ﾘ': 106,
    'ﾙ': 107,
    'ﾚ': 108,
    'ﾛ': 109,
    'ﾜ': 110,
    'ｦ': 111,
    'ﾝ': 112,
    '゛': 113,
    '゜': 115,
    'HH': 0,
}

def audioInput(stream, fs):
    ret = stream.read(fs, exception_on_overflow = False)
    ret = np.frombuffer(ret, dtype='int16') / 32768
    return ret
    
def get_db(data, fs):
    squaressum = 0
    for i in range(fs):
        squaressum += data[i] * data[i]
        
    meansquare = squaressum / (fs/2)

    rms = math.sqrt(meansquare)
    decibel = -90
    try:
        decibel = 20 * math.log10(rms)
    except ValueError:
        decibel = -90

    return int(decibel)

async def sendloop():
    global charqueue, char_digit
    while True:
        if len(charqueue) > 0:
            char = charqueue.pop(0)
            print('send ', char)
            if osc_chars.get(char) != None:
                if char == '=' or char == 'HH':
                    print('clear')
                    char_digit = 1
                    client.send_message('/avatar/parameters/MC_Apply', False)
                    await asyncio.sleep(0.3)
                    client.send_message('/avatar/parameters/MC_Digit', 0)
                    await asyncio.sleep(0.03)
                    client.send_message('/avatar/parameters/MC_Apply', True)
                    await asyncio.sleep(0.5)
                else:
                    client.send_message('/avatar/parameters/MC_Apply', False)
                    await asyncio.sleep(0.3)
                    client.send_message('/avatar/parameters/MC_Digit', char_digit)
                    await asyncio.sleep(0.03)
                    client.send_message('/avatar/parameters/MC_Text', osc_chars.get(char) / 127)
                    await asyncio.sleep(0.03)
                    client.send_message('/avatar/parameters/MC_Apply', True)
                    await asyncio.sleep(0.5)
                    char_digit += 1
                    if char_digit > 16: char_digit = 1
        await asyncio.sleep(0.1)


async def mainloop():
    global samplerate, index, fs, threshold, wabuncode, morsecode, isWabun, charqueue, dot_length
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=samplerate,
                     input=True,
                     output=True,
                     input_device_index=index,
                     frames_per_buffer=fs)

    b_state = False
    cont = 0
    st = ''
    already_sp = True
    while True:
        data = audioInput(stream, fs)
        s = get_db(data, fs)
        ison = s > threshold

        if ison == b_state:
            cont += 1
            if not ison and cont > dot_length * 6:
                ret = None
                if isWabun : ret = wabuncode.get(st)
                else       : ret = morsecode.get(st)
                if not isWabun and ret == 'ﾎﾚ' :
                    isWabun = True
                elif isWabun and ret == 'ﾗﾀ':
                    isWabun = False
                else:
                    if ret != None:
                        if ret == 'HH':
                            charqueue.append(ret)
                        else:
                            charqueue.extend(ret)
                        if ret == '=' or ret == 'HH':
                            already_sp = True
                    elif not already_sp :
                        charqueue.append(' ')
                        already_sp = True
                st = ''
                cont = 0
        else:
            if b_state:
                if cont < dot_length: st+='.'
                else                : st+='-'
            else:
                if cont > dot_length * 2:
                    ret = None
                    if isWabun : ret = wabuncode.get(st)
                    else       : ret = morsecode.get(st)
                    if not isWabun and ret == 'ﾎﾚ' :
                        isWabun = True
                    elif isWabun and ret == 'ﾗﾀ':
                        isWabun = False
                    else:
                        if ret != None:
                            if ret == 'HH':
                                charqueue.append(ret)
                            else:
                                charqueue.extend(ret)
                            if ret == '=' or ret == 'HH':
                                already_sp = True
                        elif not already_sp :
                            charqueue.append(' ')
                            already_sp = True
                    st = ''
            cont = 0
            already_sp = False
        b_state = ison
        await asyncio.sleep(0.01)

async def main():
    await asyncio.gather(mainloop(), sendloop())

if __name__ == '__main__':
    asyncio.run(main())
