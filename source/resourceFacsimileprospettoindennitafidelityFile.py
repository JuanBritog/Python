def readFile(file_path, logger):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            try:
                #ruolo :MBFA – MBSA – MBWA
                ndg, data,ruolo, copertuAssMorte, copertuAssInfort = line.strip().split(';')
                yield ndg, data ,ruolo , copertuAssMorte, copertuAssInfort
            except ValueError:
                logger.error(f"Invalid line format: {line.strip()}. Skipping this entry.")
                continue
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        yield None