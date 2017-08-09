def str2bool(str):
    true_list = [True, 'true', 'True', 1, 'yes', 'y']

    if str in true_list:
        return True
    else:
        return False