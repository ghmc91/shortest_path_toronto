# Classe para definir os pontos de endereço

class AddressPoints:
    
    def __init__(self):
        import pickle
        self.ap_map = pickle.load(open('mapas/addresspoints.p', 'rb'))
        self.replaceMap = {
            'road':'rd',
            'street':'st',
            'lane':'ln',
            'saint':'st',
            'avenue':'ave',
            'boulevard':'blvd',
            'crescent':'cres',
            'court':'crt',
            'circle':'crcl',
            'west' : 'w',
            'east': 'e',
            'north': 'n',
            'south':'s'
        }
        
    def translate(self, address):
        # Tentativa de formatar o endereço correspondente à convenção do arquivo do ponto de endereço.
        import string
        address = address.lower()
        address = ''.join([letter for letter in address if letter not in set(string.punctuation)])
        address = ' '.join([word if word not in self.replaceMap else self.replaceMap[word] for word in address.split(' ')])
        return address
        
    def get(self, address):
        # Retorna o registro do endereço
        # Argumentos: address - string - endereço legível para humanos
        return self.ap_map[self.translate(address)]