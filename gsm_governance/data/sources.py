from dataclasses import dataclass
@dataclass(frozen=True)
class DataSource:
    name:str; indicator:str; dimension:str; url:str; theoretical_min:float; theoretical_max:float
SOURCES={
"accountability":DataSource("V-Dem","Liberal Democracy Index","accountability","https://www.v-dem.net",0,1),
"competence":DataSource("World Bank WGI","Government Effectiveness","competence","https://info.worldbank.org/governance/wgi/",-2.5,2.5),
"cohesion":DataSource("World Justice Project","Rule of Law Index","cohesion","https://worldjusticeproject.org",0,1),
"continuity":DataSource("UNDP","Human Development Index","continuity","https://hdr.undp.org",0,1),
"learning":DataSource("Our World in Data","Government Service Satisfaction","learning","https://ourworldindata.org",0,100)}
DENMARK_RAW={"accountability":.883,"competence":2.11,"cohesion":.90,"continuity":.962,"learning":72.4}
