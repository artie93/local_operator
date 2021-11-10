import os
import platform
import yaml
from string import Template
from subprocess import Popen, PIPE


def set_compiler(compiler):
    try:
        with Popen([compiler["cpp"][0], "-dumpversion"], stdout=PIPE) as p:
            compiler_version = p.stdout.read().decode("ascii").strip()
    except:
        compiler_version = compiler["version"][0]

        os.environ["CXX"] = compiler["cpp"][0]
        os.environ["CC"] = compiler["cc"][0]
    return compiler_version


def parse_compiler_configuration(file):
    # Read Compiler configuration file
    with open(file, "r") as stream:
        try:
            compilers = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return compilers


def machine_name():
    # Set architecture from platform
    try:
        with open("/sys/devices/cpu/caps/pmu_name", "r") as pmu:
            machine = pmu.readlines()[0].strip()
    except:
        machine = platform.processor()


def create_ouput(problem):
    header = "machine,problem,compiler,version,flags,degree,rank,ncells,time"
    path = "output/"
    out_file = path + str(problem) + ".txt"

    if not os.path.exists(out_file):
        os.mkdir(path)
        with open(out_file, "a") as f:
            f.write(header)
    return out_file


def run_ffcx(problem: str, degree: int, nrepeats: int,
             flag: list, matrix_free: bool):
    try:
        import ffcx
        import ffcx.codegeneration
    except ImportError:
        print("ffcx is no available")

    os.environ["UFC_INCLUDE_DIR"] = ffcx.codegeneration.get_include_path()

    with open("forms/" + problem + ".ufl", 'r') as f:
        src = Template(f.read())
        d = {'degree': str(degree), 'vdegree': str(degree + 1)}
        result = src.substitute(d)
        with open("problem.ufl", "w") as f2:
            f2.writelines(result)

    if matrix_free:
        run = "./ffcx/build/benchmark-mf"
    else:
        run = "./ffcx/build/benchmark"

    build = f"cd ffcx && rm -rf build && mkdir build && cd build && cmake -DCMAKE_C_FLAGS={flag} -DCMAKE_CXX_FLAGS={flag} .. && make"

    if os.system(f"ffcx problem.ufl -o ffcx/") != 0:
        raise RuntimeError("ffcx failed")
    if os.system(build) != 0:
        raise RuntimeError("build failed")
    result = []
    for i in range(nrepeats):
        with Popen(["./ffcx/build/benchmark-mf"], stdout=PIPE) as p:
            out = p.stdout.read().decode("ascii").strip()
        result.append(out)

    return result
