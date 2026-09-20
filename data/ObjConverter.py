from data.Shapes2d import Shape2D, Polygon, Line, Point, BezierCurve

class ObjConverter:
    @staticmethod
    def _export(filepath: str, shapes: list[Shape2D]):
        with open(filepath, 'w') as file:
            file.write("# Viewport 2D file\n")

            global_vertex_id = 1 # Será responsável por enumerar as vértices do arquivo todo

            for shape in shapes:
                file.write(f"\no {shape.name}\n")
                file.write(f"# color {shape.color}\n")

                object_indexes = []
                for i in range(shape.cord_matrix_world.shape[0]):
                    x = shape.cord_matrix_world[i, 0]
                    y = shape.cord_matrix_world[i, 1]
                    file.write(f"v {x} {y} 0.0\n") # Em arquivo .obj precisamos inserir o Z também, que para 2D é 0
                    object_indexes.append(global_vertex_id)
                    global_vertex_id += 1

                index_str = " ".join(map(str, object_indexes))
                if isinstance(shape, Point):
                    file.write(f"p {index_str}\n")
                elif isinstance(shape, Line):
                    file.write(f"l {index_str}\n")
                elif isinstance(shape, Polygon):
                    file.write(f"f {index_str}\n")
                elif isinstance(shape, BezierCurve):
                    file.write(f"b {index_str}\n")

    @staticmethod
    def _import(filepath: str) -> list[Shape2D]:
        loaded_shapes: list[Shape2D] = []

        with open(filepath, 'r') as file:
            vertex=[]
            current_name="Object"
            current_color="#000000"

            for line in file:
                parts = line.strip().split()
                if not parts:
                    continue

                prefix = parts[0]

                if prefix == "v": # dados de vértices
                    vertex.append((float(parts[1]), float(parts[2]))) # Ignoramos o Z

                elif prefix == "o": # nome do objeto
                    current_name = " ".join(parts[1:]) # É feito assim para caso o nome tenha espaços

                elif prefix == "#" and len(parts) >= 3 and parts[1] == "color": # cor do objeto
                    current_color = parts[2]

                # tipos de objeto
                elif prefix == "p": 
                    index = int(parts[1]) - 1
                    shape = Point(current_name, [vertex[index]], current_color)
                    loaded_shapes.append(shape)

                elif prefix == "l":
                    index_1 = int(parts[1].split('/')[0]) - 1 # fazer split com / é uma especificação do formato .obj
                    index_2 = int(parts[2].split("/")[0]) - 1
                    shape = Line(current_name, [vertex[index_1], vertex[index_2]], current_color)
                    loaded_shapes.append(shape)

                elif prefix == "f":
                    index = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                    cords = [vertex[i] for i in index]
                    shape = Polygon(current_name, cords, current_color)
                    loaded_shapes.append(shape)

                elif prefix == "b":
                    index = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                    cords = [vertex[i] for i in index]
                    shape = BezierCurve(current_name, cords, current_color)
                    loaded_shapes.append(shape)

        return loaded_shapes