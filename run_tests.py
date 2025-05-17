import os
import sys
import subprocess
import filecmp
from pathlib import Path

def normalize_output(text):
    # Eliminar BOM si existe y normalizar saltos de línea
    text = text.replace('\ufeff', '')  # Eliminar BOM
    text = text.replace('\r\n', '\n')  # Normalizar CRLF a LF
    text = text.strip()  # Eliminar espacios y líneas en blanco al inicio y final
    # Normalizar múltiples líneas en blanco a una sola
    lines = [line.rstrip() for line in text.split('\n')]
    # Eliminar líneas vacías consecutivas
    result = []
    prev_empty = False
    for line in lines:
        if line.strip():
            result.append(line)
            prev_empty = False
        elif not prev_empty:
            result.append(line)
            prev_empty = True
    return '\n'.join(result)

def read_file_with_encoding(file_path):
    # Lista de codificaciones a intentar
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16le', 'utf-16be', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                return normalize_output(content)
        except UnicodeError:
            continue
    
    raise ValueError(f"No se pudo leer el archivo {file_path} con ninguna codificación conocida")

def write_file_with_encoding(file_path, content):
    # Intentar escribir en UTF-8 primero
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except UnicodeError:
        # Si falla, intentar con UTF-16
        with open(file_path, 'w', encoding='utf-16') as f:
            f.write(content)

def run_test(test_file):
    # Obtener el nombre base del archivo de prueba
    test_name = os.path.basename(test_file)
    base_name = test_name.replace('.imperat', '')
    
    # Definir las rutas de los archivos
    out_expected = os.path.join('TestCases', 'Outs', f'{base_name}.out')
    out_generated = os.path.join('Outs', f'{base_name}.out')
    
    # Crear el directorio Outs si no existe
    os.makedirs('Outs', exist_ok=True)
    
    # Ejecutar el lexer y guardar la salida
    try:
        result = subprocess.run(['python', 'lexer.py', test_file], 
                             capture_output=True, 
                             text=True,
                             encoding='utf-8')
        
        # Normalizar la salida antes de escribirla
        output = normalize_output(result.stdout)
        if result.stderr:
            output += '\n' + normalize_output(result.stderr)
            
        # Escribir la salida normalizada
        write_file_with_encoding(out_generated, output)
        
    except Exception as e:
        print(f"Error al ejecutar la prueba {test_name}: {str(e)}")
        return False
    
    # Comparar con la salida esperada
    try:
        expected = read_file_with_encoding(out_expected)
        generated = read_file_with_encoding(out_generated)
        
        if expected == generated:
            print(f"✓ {test_name}: Prueba exitosa")
            return True
        else:
            print(f"✗ {test_name}: Las salidas no coinciden")
            print("\nSalida esperada:")
            print(expected)
            print("\nSalida generada:")
            print(generated)
            return False
    except Exception as e:
        print(f"Error al comparar las salidas de {test_name}: {str(e)}")
        return False

def main():
    # Obtener todos los archivos de prueba
    test_dir = os.path.join('TestCases', 'Tests')
    test_files = sorted([f for f in os.listdir(test_dir) if f.endswith('.imperat')])
    
    if not test_files:
        print("No se encontraron archivos de prueba en TestCase/Test")
        return
    
    # Ejecutar todas las pruebas
    total = len(test_files)
    passed = 0
    
    print(f"\nEjecutando {total} pruebas...\n")
    
    for test_file in test_files:
        full_path = os.path.join(test_dir, test_file)
        if run_test(full_path):
            passed += 1
    
    # Mostrar resumen
    print(f"\nResumen: {passed}/{total} pruebas exitosas")
    
if __name__ == "__main__":
    main() 