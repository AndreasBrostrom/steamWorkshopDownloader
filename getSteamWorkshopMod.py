#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import shutil

SCRIPTPATH    = os.path.realpath(__file__)
SCRIPTROOT    = os.path.dirname(SCRIPTPATH)
WORKDIR       = os.path.join(SCRIPTROOT,"out")

STEAMCMD      = os.path.join("steamcmd")

def check_required_tools():
    toolsMissing = False
    print("Checking tools:")
    for tool in [STEAMCMD]:
        if shutil.which(tool):
            print('> {}{}'.format(f"{tool}: ".ljust(12), shutil.which(tool)))
        else:
            print('> {}Does not exist'.format(f"{tool}: ".ljust(12), shutil.which(tool)))
            toolsMissing = True
    if toolsMissing:
        print("Error: Vital tools are missing")
        sys.exit(1)

def download_mod_files(gameid, complete_mod_list, STEAM_LOGIN, STEAM_PASS, verbose=False):
    
    print("Setting up download directories...") if verbose else ""
    if not os.path.exists(os.path.join(WORKDIR,"steamapps","workshop","content",gameid)):
        os.makedirs(os.path.join(WORKDIR,"steamapps","workshop","content",gameid))
    if not os.path.exists(os.path.join(WORKDIR,"steamapps","workshop","downloads",gameid)):
        os.makedirs(os.path.join(WORKDIR,"steamapps","workshop","downloads",gameid))
    if not os.path.exists(os.path.join(WORKDIR,"steamapps","workshop","temp",gameid)):
        os.makedirs(os.path.join(WORKDIR,"steamapps","workshop","temp",gameid))

    print("Assembling command and list") if verbose else ""
    print(" ".join(complete_mod_list)) if verbose else ""

    login_cmd = [
        STEAMCMD,
        '+force_install_dir', WORKDIR,
        '+login', STEAM_LOGIN, STEAM_PASS,
    ]

    mods_cmd_parts = []
    for mod_id in complete_mod_list:
        mods_cmd_parts.extend(['+workshop_download_item', gameid, mod_id, 'validate'])

    full_cmd = login_cmd + ['+quit'] +mods_cmd_parts

    if verbose:
        str_cmd = ' '.join(full_cmd)
        if not STEAM_LOGIN == "":
            str_cmd = str_cmd.replace(STEAM_LOGIN,'***')
        if not STEAM_PASS == "":
            str_cmd = str_cmd.replace(STEAM_PASS,'***')
        print('>', str_cmd)

    if verbose:
        stdoutVar=None
    else:
        stdoutVar=subprocess.DEVNULL

    print(f"Connecting and downloading workshop mods...")
    print ("NOTE: If it locks up here you steam guard code will be required below:") if not verbose else ""
    try:
        subprocess.run(full_cmd, shell=(os.name == 'nt'), check=True, stdout=stdoutVar)
        print()
        for mod in complete_mod_list:
            if os.path.exists(os.path.join(WORKDIR,"steamapps","workshop","content",gameid,mod)):
                print(f"> Mod {mod} successfully downloaded...")
            else:
                print(f"> Mod {mod} has failed to be downloaded...")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download mods: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog='getWorkshopMod',
        description='Download selected mod',
        epilog='')

    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-p', '--password', type=str)
    parser.add_argument('-C', '--config', type=str)
    parser.add_argument('-g','--gameid', type=str, help='Steam Game Id', required=True)
    parser.add_argument('-l','--list', nargs='+', help='ID of workshop mods', required=True)
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()
    
    # handle Config
    serverConfig = {
        "username": "",
        "password": ""
    }
    if args.config:
        try: 
            configFile = open(args.config)
        except FileNotFoundError as e:
            print(e);sys.exit(1)
        configFileDict = json.load(configFile)
        configFile.close()
        if "username" in configFileDict:
            serverConfig.update({"username": configFileDict["username"]})
        if "password" in configFileDict:
            serverConfig.update({"password": configFileDict["password"]})
    if args.username:
        serverConfig.update({"username": args.username})
    if args.password:
        serverConfig.update({"password": args.password})

    # Checking required tools
    check_required_tools()


    # Create download and project working folder
    if not os.path.exists(WORKDIR):
        os.makedirs(WORKDIR)

    # Download test steam and then start downloading
    subprocess.run([STEAMCMD, '+quit'], shell=(os.name == 'nt'), check=False,stdout=subprocess.DEVNULL)
    download_mod_files(args.gameid, args.list, serverConfig['username'], serverConfig["password"], args.verbose)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted")
        sys.exit(1)