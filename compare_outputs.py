import os
import subprocess
import difflib
import sys

# Global variable to store the parser script path
PARSER_SCRIPT_PATH = None

def run_parser(test_file):
    """Ejecuta el script parser especificado con el archivo de prueba y retorna la salida"""
    if PARSER_SCRIPT_PATH is None:
        print("Error: El script del parser no ha sido especificado.")
        sys.exit(1)

    try:
        result = subprocess.run(['python', PARSER_SCRIPT_PATH, test_file],
                              capture_output=True,
                              text=True,
                              check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando {PARSER_SCRIPT_PATH} con {test_file}:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: No se encontró el script del parser en la ruta '{PARSER_SCRIPT_PATH}'.")
        sys.exit(1)


def get_expected_output(test_file):
    """Obtiene la salida esperada del archivo correspondiente"""
    output_file = test_file.replace('Tests', 'Out').replace('.imperat', '.out')

    if not os.path.exists(output_file):
        print(f"Advertencia: No se encontró el archivo de salida esperado {output_file}")
        return None

    try:
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError:
            with open(output_file, 'r', encoding='utf-16') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error leyendo {output_file}: {str(e)}")
        return None

def compare_outputs(actual, expected, test_file):
    """Compara las salidas y retorna True si coinciden, False en caso contrario"""
    if actual is None or expected is None:
        return False

    return actual == expected

def main():
    global PARSER_SCRIPT_PATH # Declare that we are using the global variable

    test_dir = 'CasosDePrueba/Tests'

    # Check for arguments: first argument should be the parser script
    if len(sys.argv) < 2:
        print("Uso: python compare_outputs.py <ruta_al_parser.py> [archivo_de_prueba.imperat]")
        print("Ejemplo: python compare_outputs.py parseBeta.py")
        print("Ejemplo: python compare_outputs.py parseBeta.py prueba1.imperat")
        sys.exit(1)

    PARSER_SCRIPT_PATH = sys.argv[1]

    # Validate if the parser script exists
    if not os.path.exists(PARSER_SCRIPT_PATH):
        print(f"Error: El script del parser '{PARSER_SCRIPT_PATH}' no se encontró.")
        sys.exit(1)
    if not PARSER_SCRIPT_PATH.endswith('.py'):
        print(f"Error: El script del parser debe ser un archivo .py: '{PARSER_SCRIPT_PATH}'.")
        sys.exit(1)


    test_files_to_run = []
    # If a third argument is provided, it's a specific test file
    if len(sys.argv) > 2:
        single_test_file_name = sys.argv[2]
        full_path_to_single_test = os.path.join(test_dir, single_test_file_name)

        if not os.path.exists(full_path_to_single_test):
            print(f"Error: El archivo de prueba '{single_test_file_name}' no se encontró en '{test_dir}'.")
            sys.exit(1)
        if not single_test_file_name.endswith('.imperat'):
            print(f"Error: El archivo de prueba '{single_test_file_name}' no es un archivo .imperat.")
            sys.exit(1)

        test_files_to_run = [single_test_file_name]
        print(f"\nEjecutando prueba única '{single_test_file_name}' con el parser '{PARSER_SCRIPT_PATH}'\n")
    else:
        # If no specific test file, run all .imperat files
        test_files_to_run = [f for f in os.listdir(test_dir) if f.endswith('.imperat')]
        test_files_to_run.sort()

        if not test_files_to_run:
            print("No se encontraron archivos de prueba")
            sys.exit(0)

        print(f"\nEjecutando {len(test_files_to_run)} pruebas con el parser '{PARSER_SCRIPT_PATH}'...\n")

    total = len(test_files_to_run)
    passed_files = []
    failed_files = []

    for test_file in test_files_to_run:
        full_path = os.path.join(test_dir, test_file)

        actual_output = run_parser(full_path)
        expected_output = get_expected_output(full_path)

        if compare_outputs(actual_output, expected_output, test_file):
            passed_files.append(test_file)
        else:
            failed_files.append(test_file)

    print(f"\n--- Resumen de Pruebas ---")
    print(f"Total de pruebas: {total}\n")

    if passed_files:
        print(f"Pruebas exitosas ({len(passed_files)}):")
        for f in passed_files:
            print(f"  ✓ {f}")
    else:
        print("No hay pruebas exitosas.")

    print("\n")

    if failed_files:
        print(f"Pruebas fallidas ({len(failed_files)}):")
        for f in failed_files:
            print(f"  ✗ {f}")
    else:
        print("No hay pruebas fallidas.")

    sys.exit(0 if not failed_files else 1)

if __name__ == '__main__':
    main()