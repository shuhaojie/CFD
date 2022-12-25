import bcrypt


def set_password(pw):
    pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
    password_hash = pwhash.decode('utf8')  # decode the hash to prevent is encoded twice
    return password_hash
