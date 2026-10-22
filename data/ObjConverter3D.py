from data.Shapes3d import Shape3D, Point3DRender, Polygon3D, Point3D, Window3D


class ObjConverter3D:
    @staticmethod
    def _export(filepath: str, shapes: list[Shape3D]):
        with open(filepath, 'w') as file:
            file.write("# Viewport 2D file\n")

            global_vertex_id = 1 # Será responsável por enumerar as vértices do arquivo todo

            for shape in shapes:
                if(isinstance(shape, Window3D)): continue
                file.write(f"\no {shape.name}\n")
                # file.write(f"# color {shape.color}\n")

                object_indexes = []
                for i in range(shape.cord_matrix_world.shape[0]):
                    x = shape.cord_matrix_world[i, 0]
                    y = shape.cord_matrix_world[i, 1]
                    z = shape.cord_matrix_world[i, 2]
                    file.write(f"v {x} {y} {z}\n") # Em arquivo .obj precisamos inserir o Z também, que para 2D é 0
                    object_indexes.append(global_vertex_id)
                    global_vertex_id += 1

                if isinstance(shape, Polygon3D):
                    for point0, point1 in shape.edges:
                        file.write(f"l {point0} {point1}\n") # Lista de linhas para wireframe

                index_str = " ".join(map(str, object_indexes))
                if isinstance(shape, Point3DRender):
                    file.write(f"p {index_str}\n")
                elif isinstance(shape, Polygon3D):
                    file.write(f"f {index_str}\n")

    @staticmethod
    def _import(filepath: str) -> list[Shape3D]:
        loaded_shapes: list[Shape3D] = []

        with open(filepath, 'r') as file:
            vertex=[]
            edge=[]
            current_name="Object"
            current_color="#000000"

            for line in file:
                parts = line.strip().split()
                if not parts:
                    continue

                prefix = parts[0]

                if prefix == "v": # dados de vértices
                    vertex.append(Point3D((float(parts[1]), float(parts[2]), float(parts[3])))) # Ignoramos o Z

                elif prefix == "o": # nome do objeto
                    current_name = " ".join(parts[1:]) # É feito assim para caso o nome tenha espaços

                # tipos de objeto
                elif prefix == "p": 
                    index = int(parts[1]) - 1
                    shape = Point3DRender(current_name, [vertex[index]], current_color)
                    loaded_shapes.append(shape)

                elif prefix == "l":
                    edge.append((float(parts[1]), float(parts[2])))

                elif prefix == "f":
                    index = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                    cords = [vertex[i] for i in index]
                    shape = Polygon3D(current_name, cords, edge, current_color)
                    loaded_shapes.append(shape)

                # elif prefix == "b":
                #     index = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                #     cords = [vertex[i] for i in index]
                #     shape = BezierCurve(current_name, cords, current_color)
                #     loaded_shapes.append(shape)
                #
                # elif prefix == "s":
                #     index = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                #     cords = [vertex[i] for i in index]
                #     shape = BSplineCurve(current_name, cords, current_color)
                #     loaded_shapes.append(shape)


        return loaded_shapes