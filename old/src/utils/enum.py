from enum import Enum

class WoundType(str, Enum):
    ud = "Úlcera do Pé Diabético"
    up = "Lesão por Pressão"
    uv = "Úlcera Venosa"
    ua = "Úlcera Arterial"
    ft = "Ferida por Trauma"
    fc = "Ferida Cirúrgica"
    qm = "Queimadura"
    os = "Ostomia"
    st = "Skin Tear"
    fs = "Fístula"
    fn = "Ferida Neoplásica"
    fl = "Flebite"

class WoundSize(str, Enum):
    size_0 = "0 cm²"
    size_1 = "Menor que 0,3 cm²"
    size_2 = "0,3 - 0,6 cm²"
    size_3 = "0,7 - 1 cm²"
    size_4 = "1,1 - 2 cm²"
    size_5 = "2,1 - 3 cm²"
    size_6 = "3,1 - 4 cm²"
    size_7 = "4,1 - 8 cm²"
    size_8 = "8,1 - 12 cm²"
    size_9 = "12,1 - 24 cm²"
    size_10 = "Maior que 24 cm²"

class WoundLocation(str, Enum):
    cb = "Cabeça"
    fc = "Face"
    pc = "Pescoço"
    pt = "Peito"
    ab = "Abdome"
    ds = "Dorso"
    pr = "Região Perineal"
    ms = "Membro Superior"
    mi = "Membro Inferior"

class WoundEdges(str, Enum):
    in_ = "Indefinidas, não visíveis claramente"
    df = "Definidas, contorno claramente visível, aderidas, niveladas com a base da ferida"
    na = "Bem definidas, não aderidas à base da ferida"
    cu = "Bem definidas, não aderidas à base, enrolada, espessada"
    fb = "Bem definidas, fibróticas, com crostas e/ou hiperqueratose"

class TissueType(str, Enum):
    tc = "Tecido cicatrizado"
    te = "Tecido de epitelização"
    tg = "Tecido de granulação"
    td = "Tecido desvitalizado"
    tn = "Tecido necrótico"

class SmokeFrequency(str, Enum):
    never = "Nunca"
    past = "Pregresso"
    up_to_10_per_day = "Até 10 cigarros por dia"
    more_than_10_per_day = "Mais que 10 cigarros por dia"

class SkinAroundTheWound(str, Enum):
    in_ = "Inchaço"
    l2 = "Eritema menor que 2 cm"
    g2 = "Eritema maior que 2 cm"

class ExudateType(str, Enum):
    serous = "Seroso"
    sanguineous = "Sanguinolento"
    purulent = "Purulento"
    serosanguineous = "Serosanguinolento"
    fetid = "Fétido"
    absent = "Ausente"

class ExudateAmount(str, Enum):
    none = "Nenhum"
    little = "Pouco"
    medium = "Médio"
    much = "Muito"

