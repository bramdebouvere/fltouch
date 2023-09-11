import mixer

TransliterateMap = {
    # ASCII Extended
    u'ã': 'a',
    u'Ã': 'A',
    u'à': 'a',
    u'À': 'A',
    u'á': 'a',
    u'Á': 'A',
    u'€': 'EUR',
    u'Ž': 'Z',
    u'ž': 'z',
    u'œ': 'oe',
    u'é': 'e',
    u'É': 'E',
    u'è': 'e',
    u'È': 'E',
    u'ê': 'e',
    u'Ê': 'E',
    u'ë': 'e',
    u'Ë': 'E',
    u'ì': 'i',
    u'Ì': 'I',
    u'í': 'i',
    u'Í': 'I',
    u'î': 'i',
    u'Î': 'I',
    u'ï': 'i',
    u'Ï': 'I',
    u'ù': 'u',
    u'Ù': 'U',
    u'ú': 'u',
    u'Ú': 'U',
    u'û': 'u',
    u'Û': 'U',
    u'ü': 'u',
    u'Ü': 'U',
    u'ý': 'y',
    u'Ý': 'Y',
    # International
    u'å': 'aa',
    u'Å': 'Aa',
    u'ä': 'ae',
    u'Ä': 'Ae',
    u'æ': 'ae',
    u'Æ': 'Ae',
    u'Ç': 'Ts',
    u'ç': 'ts',
    u'ñ': 'n',
    u'Ñ': 'N',
    u'ð': 'dh',
    u'ö': 'oe',
    u'Ö': 'Oe',
    u'ø': 'oe',
    u'Ø': 'Oe',
    u'õ': 'o',
    u'Õ': 'O',
    u'ü': 'ue',
    u'Ü': 'Ue',
    u'þ': 'th',
    u'Þ': 'Th',
    u'ß': 'ss',
    # Cyrillic (Russia)
    '\u0410': 'A', '\u0430': 'a',
    '\u0411': 'B', '\u0431': 'b',
    '\u0412': 'V', '\u0432': 'v',
    '\u0413': 'G', '\u0433': 'g',
    '\u0414': 'D', '\u0434': 'd',
    '\u0415': 'E', '\u0435': 'e',
    '\u0416': 'Zh', '\u0436': 'zh',
    '\u0417': 'Z', '\u0437': 'z',
    '\u0418': 'I', '\u0438': 'i',
    '\u0419': 'I', '\u0439': 'i',
    '\u041a': 'K', '\u043a': 'k',
    '\u041b': 'L', '\u043b': 'l',
    '\u041c': 'M', '\u043c': 'm',
    '\u041d': 'N', '\u043d': 'n',
    '\u041e': 'O', '\u043e': 'o',
    '\u041f': 'P', '\u043f': 'p',
    '\u0420': 'R', '\u0440': 'r',
    '\u0421': 'S', '\u0441': 's',
    '\u0422': 'T', '\u0442': 't',
    '\u0423': 'U', '\u0443': 'u',
    '\u0424': 'F', '\u0444': 'f',
    '\u0425': 'Kh', '\u0445': 'kh',
    '\u0426': 'Ts', '\u0446': 'ts',
    '\u0427': 'Ch', '\u0447': 'ch',
    '\u0428': 'Sh', '\u0448': 'sh',
    '\u0429': 'Shch', '\u0449': 'shch',
    '\u042a': ''', '\u044a': ''',
    '\u042b': 'Y', '\u044b': 'y',
    '\u042c': ''', '\u044c': ''',
    '\u042d': 'E', '\u044d': 'e',
    '\u042e': 'Iu', '\u044e': 'iu',
    '\u042f': 'Ia', '\u044f': 'ia',
    # Cyrillic (Ukraine)
    u'є': 'ye',
    u'ж': 'zh',
    u'ї': 'yi',
    u'х': 'kh',
    u'ц': 'ts',
    u'ч': 'ch',
    u'ш': 'sh',
    u'щ': 'shch',
    u'ю': 'ju',
    u'я': 'ja',
    u'Є': 'Ye',
    u'Ж': 'Zh',
    u'Ї': 'Yi',
    u'Х': 'Kh',
    u'Ц': 'Ts',
    u'Ч': 'Ch',
    u'Ш': 'Sh',
    u'Щ': 'Shch',
    u'Ю': 'Ju',
    u'Я': 'Ja',
    # Serbian
    u'љ': 'lj',
    u'њ': 'nj',
    u'џ': 'dž',
    u'Љ': 'Lj',
    u'Њ': 'Nj',
    u'Џ': 'Dž'
}

def GetAsciiSafeTrackName(index: int, maxLength: int = 0) -> str:
    ''' Gets an ASCII compatible track name value '''
    unicodeTrackName = mixer.getTrackName(index, maxLength)
    transliterated = TransliterateToAscii(unicodeTrackName)
    if maxLength > 0:
        transliterated = transliterated[:maxLength]
    return transliterated

def TransliterateToAscii(unicodeValue):
    ''' Gets an ASCII compatible value for non-ascii characters (Basic Transliteration) '''
    converted = ''
    for char in unicodeValue:
        transchar = ''
        if char in TransliterateMap: # not ascii compatible, but is known in the dictionairy
            transchar = TransliterateMap[char]
        elif 32 <= ord(char) < 127: # ascii printable characters
            transchar = char
        else: # Screens are small, so just ignore values it does not know how to transliterate
            transchar = ''
        converted += transchar
    return converted
