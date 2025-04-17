
def get_names():
    with open('app/api/NOMES_PESSOAS.csv', 'r') as file:
        names = file.read().splitlines()

    # csv structure: lastname, firstname, extra info
    # return: firstname lastname
    names = [name.split(',')[1] + " " + name.split(',')[0] for name in names]
    names = [name.replace('"', '') for name in names]
    names = [name for name in names if name != "Not. autor Descrição"]

    return {"names": names}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
