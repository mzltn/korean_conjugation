# -*- coding: utf-8 -*-

# (C) 2010 Dan Bravender - licensed under the AGPL 3.0

try:
    unicode
except NameError:
    unicode = str  # In Python 3, use str as a replacement for unicode
    unichr = chr  # In Python 3, use chr instead of unichr

class Geulja(unicode):
    u'''Geulja is used to track modifications that have been made to
        characters. Currently, it keeps track of characters' original
        padchims (for ㄷ -> ㄹ irregulars) and if the character has
        no padchim but should be treated as if it does (for ㅅ 
        irregulars). When substrings are extracted the Geulja class 
        keeps these markers for the last character only.
     '''
    hidden_padchim = False
    original_padchim = None
    
    def __getitem__(self, index):
        g = Geulja(unicode.__getitem__(self, index))
        # only keep the hidden padchim marker for the last item
        if index == -1:
            g.hidden_padchim = self.hidden_padchim
            g.original_padchim = self.original_padchim
        return g

def is_hangeul(character):
    assert len(character) == 1, 'is_hangeul only checks characters with a length of 1'

    if ord(character) >= ord(u'가') and ord(character) <= ord(u'힣'):
        return True
    return False

def find_vowel_to_append(string):
    for character in reversed(string):
        if character in [u'뜨', u'쓰', u'트']:
            return u'어'
        if vowel(character) == u'ㅡ' and not padchim(character):
            continue
        elif vowel(character) in [u'ㅗ', u'ㅏ', u'ㅑ']:
            return u'아'
        else:
            return u'어'
    return u'어'

# Equations lifted directly from:
# http://www.kfunigraz.ac.at/~katzer/korean_hangul_unicode.html

def join(lead, vowel, padchim=None):
    '''join returns the unicode character that is composed of the
       lead, vowel and padchim that are passed in.
    '''
    lead_offset = ord(lead) - ord(u'ᄀ')
    vowel_offset = ord(vowel) - ord(u'ㅏ')
    if padchim:
        padchim_offset = ord(padchim) - ord(u'ᆨ')
    else:
        padchim_offset = -1
    return unichr(padchim_offset + (vowel_offset) * 28 + (lead_offset) * 588 + \
                  44032 + 1)

def lead(character):
    '''lead returns the first consonant in a geulja
    '''
    return unichr(int((ord(character) - 44032) / 588) + 4352)

def vowel(character):
    padchim_character = padchim(character)
    # padchim returns a character or True if there is a hidden padchim, 
    # but a hidden padchim doesn't make sense for this offset
    if not padchim_character or padchim_character == True:
        padchim_offset = -1
    else:
        padchim_offset = ord(padchim_character) - ord(u'ᆨ')
    return unichr(int(((ord(character) - 44032 - padchim_offset) % 588) / 28)+ \
                  ord(u'ㅏ'))

def padchim(character):
    '''padchim returns the unicode padchim (the bottom) of a geulja.
    '''
    if getattr(character, u'hidden_padchim', False):
        return True
    if getattr(character, u'original_padchim', False):
        return character.original_padchim
    p = unichr(((ord(character) - 44032) % 28) + ord(u'ᆨ') - 1)
    if ord(p) == 4519:
        return None
    else:
        return p

def match(character, l='*', v='*', p='*'):
    '''match is a helper function that simplifies testing if
       geulja match patterns. * is used to represent any vowel or
       consonant.
    '''
    return (lead(character) == l or l == u'*') and \
           (vowel(character) == v or v == u'*') and \
           (padchim(character) == p or p == u'*')
