# Classe para encontrar o caminho mais curto

class RoadGraph:
    
    def __init__(self):
        import pickle
        from AddressPoints import AddressPoints
        self.G = pickle.load(open('mapas/roadgraph.p', 'rb'))
        self.AddressPoints = AddressPoints()
        self.torontoBoundary = pickle.load(open('mapas/torontoboundary.p', 'rb'))
        
    def get_boundary(self):
        return {'toronto': self.torontoBoundary}
        
    def get_cli(self, cli_id):
        return self.G.node[cli_id]

    def get_cl(self, *args):
        # Obter registro de linha central por identificação de linha central (geo) id ou duas interseções de linha central (int)
        if len(args) == 2:
            return self.G[args[0]][args[1]]
        elif len(args) == 1:
            for e in self.G.edges_iter():
                cl = self.G[e[0]][e[1]]['record']
                if cl[0] == args[0]:
                    return cl
        raise KeyError
        
    def get_lat_lng_list(self, ap1, ap2, path):
        # Retorna uma lista de pontos de latitude e longitude a partir de ap1 (address point 1), seguindo o caminho e chegando a ap2
        lat_lng_list = []
        lat_lng_list.append({'lat': ap1[5], 'lng': ap1[4]})
        for i in range(0, len(path)-1):
            e = self.G[path[i]][path[i+1]]
            temp = []
            for point in e['shape']:
                temp.append({'lat':point[1], 'lng':point[0]})
            if path[i] != e['record'][11]: 
                temp.reverse()
            lat_lng_list.extend(temp)
        lat_lng_list.append({'lat': ap2[5], 'lng': ap2[4]})
        return lat_lng_list

    def best_cli_pair(self, cl1, cl2):
        # Heuristicamente determina o melhor par de interseções para obter de cl1 a cl2
        from haversine import haversine
        cli11 = self.get_cli(cl1[11])
        cli12 = self.get_cli(cl1[12])
        cli21 = self.get_cli(cl2[11])
        cli22 = self.get_cli(cl2[12])
        d = [haversine((cli11[15], cli11[16]), (cli21[15], cli21[16])), \
            haversine((cli11[15], cli11[16]), (cli22[15], cli22[16])), \
            haversine((cli12[15], cli12[16]), (cli21[15], cli21[16])), \
            haversine((cli12[15], cli12[16]), (cli22[15], cli22[16])) ]
        dmin = min(d)
        if dmin == d[0]:
            return cli11, cli21
        elif dmin == d[1]:
            return cli11, cli22
        elif dmin == d[2]:
            return cli12, cli21
        else:
            return cli12, cli22
            
    def heading(self, point1, point2):
        # Retorna uma direção geral entre point1 = (lat, lng), point2 =
        from haversine import haversine
        avg_lat = 0.5*point1[0] + 0.5*point2[0]
        avg_lng = 0.5*point2[1] + 0.5*point2[1]
        if haversine((avg_lat, point1[1]), (avg_lat, point2[1])) \
        > haversine((point1[0], avg_lng), (point2[0], avg_lng)):
            # EAST/WEST
            if point2[1] > point1[1]:
                return 'EAST'
            else:
                return 'WEST'
        else:
            # NORTH/SOUTH
            if point2[0] > point1[0]:
                return 'NORTH'
            else:
                return 'SOUTH'
            
    def get_street_side(self, heading, ap):
        address_number = int(ap[2])
        cl = self.get_cl(ap[1])
        cli_from = self.get_cli(cl[11])
        cli_to = self.get_cli(cl[12])
        cl_heading = self.heading((cli_from[16], cli_from[15]), (cli_to[16], cli_to[15]))
        
        if heading == cl_heading:
            if address_number % 2 == 0:
                if cl[5] == 'E': 
                    return 'LEFT'
                else:
                    return 'RIGHT'
            else:
                if cl[5] == 'O':
                    return 'LEFT'
                else:
                    return 'RIGHT'
        else: 
            if address_number % 2 == 0:
                if cl[5] == 'E': 
                    return 'RIGHT' 
                else:
                    return 'LEFT'
            else:
                if cl[5] == 'O':
                    return 'RIGHT'
                else:
                    return 'LEFT'
                    
    def turn(self, heading1, heading2):
        direction_map = {
            'NORTH': 1,
            'EAST': 2,
            'SOUTH' : 3,
            'WEST' : 4
        }
        difference = direction_map[heading1] - direction_map[heading2]
        if difference == -1 or difference == 3:
            return 'Turn RIGHT'
        elif difference == 1 or difference == -3:
            return 'Turn LEFT'
        elif difference == 0:
            return 'CONTINUE'
        else:
            return 'Turn' 
                
    def directions(self, ap1, ap2, path):
        directions = []
    
        # Case 1: aps estão no mesmo cl (path=[])
        if ap1[1] == ap2[1]:
            cl = self.get_cl(ap1[1])
            heading = self.heading((ap1[5], ap1[4]), (ap2[5], ap2[4]))
            directions.append("Siga " + heading + " em " + cl[2])
            directions.append("Seu destino está no " + self.get_street_side(heading, ap2))
            return directions

        # Case 2: path está 1 node long (one intersection)
        elif len(path)==1:
            if ap1[1] == ap2[1]: # same street
                cli = self.get_cli(path[0])
                heading = self.heading((ap1[5], ap1[4]), (cli[16], cli[15]))
                directions.append("Siga " + heading + \
                                  " através " + ap1[3])
                directions.append('Seu destino está no ' + self.get_street_side(ap2, heading))
                return directions

            else: # different streets
                cli = self.get_cli(path[0])
                init_heading = heading = self.heading((ap1[18], ap1[17]), (cli[16], cli[15]))
                init_street = ap1[3]
                final_heading = heading = self.heading((cli[16], cli[15]), (ap2[18], ap2[17]))
                next_street = ap2[3]
                directions.append("Siga " + init_heading + \
                                  " através " + init_street + \
                                  " para " + init_street + "/" + next_street)
                directions.append(self.turn(init_heading, final_heading) + \
                                  " em " + next_street)
                directions.append('Seu destino está no ' + self.get_street_side(final_heading, ap2))
                return directions
        else:
            # Endereço aponta para iniciar a interseção para fazer a intersecção ao cruzamento
            current_street = self.get_cl(path[0], path[1])['record'][2]
            cli_from = self.get_cli(path[0])
            cli_to = self.get_cli(path[1])
            current_heading = self.heading((cli_from[16], cli_from[15]), (cli_to[16], cli_to[15]))
            for i in range(0, len(path)-1):
                if current_street == self.get_cl(path[i], path[i+1])['record'][2]:
                    continue
                directions.append("Siga " + current_heading + \
                                    " através " + current_street + \
                                        " para " + self.get_cli(path[i])[2])
                next_street = self.get_cl(path[i], path[i+1])['record'][2]
                cli_from = self.get_cli(path[i])
                cli_to = self.get_cli(path[i+1])
                next_heading = self.heading((cli_from[16], cli_from[15]), (cli_to[16], cli_to[15]))
                directions.append(self.turn(current_heading, next_heading) + \
                                  " em " + next_street)
                current_street = next_street
                current_heading = next_heading
                
            # Terminar o ponto de intersecção
            if ap2[4] != current_street:
                cli = self.get_cli(path[-1])
                final_heading = self.heading((cli[16], cli[15]), (ap2[5], ap2[4]))
                directions.append(self.turn(current_heading, final_heading) + " em " + ap2[3])
                directions.append('Seu destino está no ' + self.get_street_side(final_heading, ap2))
            else:
                directions.append('Seu destino está no ' + self.get_street_side(current_heading, ap2))
            return directions            

    # Calculando o caminho mais curto
    def shortest_route(self, address_one, address_two):
        import networkx
        path = []
        weight = 0
        ap1 = self.AddressPoints.get(address_one)
        ap2 = self.AddressPoints.get(address_two)
        cl1 = self.get_cl(ap1[1])
        cl2 = self.get_cl(ap2[1])
        cli1, cli2 = self.best_cli_pair(cl1, cl2)
        path = networkx.dijkstra_path(self.G, cli1[0], cli2[0])
        for i in range(0, len(path)-1):
            edge = self.G[path[i]][path[i+1]]
            weight = weight + edge['weight']
        return weight, self.get_lat_lng_list(ap1, ap2, path), self.directions(ap1, ap2, path)
        