"""
##########################################################################
*
*   Copyright © 2019-2021 Akashdeep Dhar <t0xic0der@fedoraproject.org>
*
*   This program is free software: you can redistribute it and/or modify
*   it under the terms of the GNU General Public License as published by
*   the Free Software Foundation, either version 3 of the License, or
*   (at your option) any later version.
*
*   This program is distributed in the hope that it will be useful,
*   but WITHOUT ANY WARRANTY; without even the implied warranty of
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*   GNU General Public License for more details.
*
*   You should have received a copy of the GNU General Public License
*   along with this program.  If not, see <https://www.gnu.org/licenses/>.
*
##########################################################################
"""

import json
from base64 import b64decode, b64encode
from os.path import basename

import click
from tqdm import tqdm
from urllib3 import PoolManager


def filesend(servloca, attrdata):
    """
    Sends file to the provided Veritas server
    :param servloca:
    :param attrdata:
    :return:
    """
    try:
        httpobjc = PoolManager()
        with open(attrdata, "r") as fileobjc:
            contents = fileobjc.read()
        b64etext = b64encode(contents.encode()).decode()
        rgetfild = {
            "filename": basename(attrdata),
            "contents": b64etext
        }
        rqstobjc = httpobjc.request("GET", servloca + "filesend", fields=rgetfild, preload_content=False)
        respdata = ""
        progelem = tqdm(rqstobjc.stream())
        for filepeic in progelem:
            respdata += filepeic.decode()
            progelem.set_description(click.style("Sending", fg="green"))
        respdata = json.loads(respdata)
        if respdata["retnmesg"] == "FAIL":
            click.echo(
                click.style("Transfer failed", fg="red", bold=True)
            )
        elif respdata["retnmesg"] == "DONE":
            click.echo(
                click.style(respdata["tokniden"], fg="green", bold=True)
            )
    except Exception as expt:
        click.echo(click.style(str(expt), fg="red"))


def filerecv(servloca, attrdata):
    """
    Receives file from the provided Veritas server
    :param servloca:
    :param attrdata:
    :return:
    """
    try:
        httpobjc = PoolManager()
        rgetfild = {
            "tokniden": attrdata
        }
        rqstobjc = httpobjc.request("GET", servloca + "filerecv", fields=rgetfild, preload_content=False)
        respdata = ""
        progelem = tqdm(rqstobjc.stream(2))
        for filepeic in progelem:
            respdata += filepeic.decode()
            progelem.set_description(click.style("Receiving", fg="green"))
        respdata = json.loads(respdata)
        if respdata["retnmesg"] == "FAIL":
            click.echo(
                click.style("Transfer failed", fg="red", bold=True)
            )
        elif respdata["retnmesg"] == "DONE":
            filename = respdata["filename"]
            b64etext = respdata["contents"]
            contents = b64decode(b64etext.encode()).decode()
            with open(filename, "w") as fileobjc:
                fileobjc.write(contents)
            click.echo(
                click.style("Transfer successful", fg="green", bold=True)
            )
    except Exception as expt:
        click.echo(click.style(str(expt), fg="red"))


@click.command()
@click.option(
    "-l",
    "--servloca",
    "servloca",
    help="Set the service location."
)
@click.option(
    "-a",
    "--attrdata",
    "attrdata",
    help="Set the attribute value."
)
@click.option(
    "-s",
    "--filesend",
    "opertion",
    flag_value="filesend",
    help="Initiate file dispersal."
)
@click.option(
    "-r",
    "--filerecv",
    "opertion",
    flag_value="filerecv",
    help="Initiate file reception."
)
@click.version_option(
    version="0.1.0-alpha",
    prog_name=click.style("Veritas Client", fg="magenta")
)
def mainfunc(servloca, attrdata, opertion):
    """
    A reliable API service to ensure that the publication reaches you in a true and untainted manner.
    """
    try:
        click.echo(
            click.style(
                "Veritas Client v0.1.0-alpha", bold=True
            )
        )
        if opertion == "filesend":
            filesend(servloca, attrdata)
        elif opertion == "filerecv":
            filerecv(servloca, attrdata)
    except Exception as expt:
        click.echo(click.style(str(expt), fg="red"))


if __name__ == "__main__":
    mainfunc()
