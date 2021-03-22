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
from hashlib import sha256
import logging
from time import time

import click
import falcon
from falcon import __version__ as flcnvers
from werkzeug import __version__ as wkzgvers
from werkzeug import serving


main = falcon.API()
loge = logging.getLogger("werkzeug")
loge.setLevel(logging.ERROR)


class FileDispersalEndpoint(object):
    def on_get(self, rqst, resp):
        try:
            filename = rqst.get_param("filename")
            contents = rqst.get_param("contents")
            jsoncont = {
                "filename": filename,
                "contents": contents,
            }
            timestmp = str(time())
            conthxdc = sha256((contents + timestmp).encode()).hexdigest()
            with open("arcade/" + conthxdc + ".json", "w") as fileobjc:
                json.dump(jsoncont, fileobjc)
            with open("arcade/contledg.json", "r") as ledgread:
                jsonledg = json.loads(ledgread.read())
            with open("arcade/contledg.json", "w") as ledgmode:
                jsonledg[conthxdc] = {
                    "timestmp": timestmp,
                    "hxdciden": conthxdc
                }
                json.dump(jsonledg, ledgmode)
            retnjson = {
                "retnmesg": "DONE",
                "tokniden": conthxdc
            }
        except Exception as expt:
            print(expt)
            retnjson = {
                "retnmesg": "FAIL"
            }
        resp.body = json.dumps(retnjson, ensure_ascii=False)
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.status = falcon.HTTP_200


class FileReceptionEndpoint(object):
    def on_get(self, rqst, resp):
        try:
            tokniden = rqst.get_param("tokniden")
            jsoncont = {}
            with open("arcade/contledg.json", "r") as ledgread:
                jsonledg = json.loads(ledgread.read())
            if tokniden in jsonledg.keys():
                with open("arcade/" + tokniden + ".json", "r") as fileobjc:
                    jsoncont = fileobjc.read()
                jsoncont = json.loads(jsoncont)
                retnjson = {
                    "retnmesg": "DONE",
                    "filename": jsoncont["filename"],
                    "contents": jsoncont["contents"]
                }
            else:
                print(expt)
                retnjson = {
                    "retnmesg": "FAIL"
                }
        except Exception as expt:
            print(expt)
            retnjson = {
                "retnmesg": "FAIL"
            }
        resp.body = json.dumps(retnjson, ensure_ascii=False)
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.status = falcon.HTTP_200


class LedgerReceptionEndpoint(object):
    def on_get(self, rqst, resp):
        try:
            with open("arcade/contledg.json", "r") as ledgread:
                jsonledg = json.loads(ledgread.read())
            retnjson = {
                "retnmesg": "DONE",
                "jsonledg": jsonledg
            }
        except Exception as expt:
            print(expt)
            retnjson = {
                "retnmesg": "FAIL"
            }
        resp.body = json.dumps(retnjson, ensure_ascii=False)
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.status = falcon.HTTP_200


@click.command()
@click.option(
    "-p",
    "--portdata",
    "portdata",
    help="Set the port value [0-65536].",
    default="6969"
)
@click.option(
    "-6",
    "--ipprotv6",
    "netprotc",
    flag_value="ipprotv6",
    help="Start the server on an IPv6 address."
)
@click.option(
    "-4",
    "--ipprotv4",
    "netprotc",
    flag_value="ipprotv4",
    help="Start the server on an IPv4 address."
)
@click.version_option(
    version="0.1.0-alpha",
    prog_name=click.style("Veritas Server", fg="magenta")
)
def mainfunc(portdata, netprotc):
    """
    A reliable API service to ensure that the publication reaches you in a true and untainted manner.
    """
    try:
        click.echo(
            click.style(
                "Veritas Server v0.1.0-alpha", bold=True
            )
        )
        netpdata = ""
        if netprotc == "ipprotv6":
            click.echo(" * " + click.style("IP version        ", fg="magenta") + ": " + "6")
            netpdata = "::"
        elif netprotc == "ipprotv4":
            click.echo(" * " + click.style("IP version        ", fg="magenta") + ": " + "4")
            netpdata = "0.0.0.0"
        click.echo(
            " * " + click.style("Reference URI     ", bold=True) + ": " + "http://" + netpdata + ":" + portdata +
            "/" + "\n" +
            " * " + click.style("Endpoint service  ", bold=True) + ": " + "Falcon v" + flcnvers + "\n" +
            " * " + click.style("HTTP server       ", bold=True) + ": " + "Werkzeug v" + wkzgvers
        )
        filesend = FileDispersalEndpoint()
        filerecv = FileReceptionEndpoint()
        ledgrecv = LedgerReceptionEndpoint()
        main.add_route("/filesend", filesend)
        main.add_route("/filerecv", filerecv)
        main.add_route("/ledgrecv", ledgrecv)
        serving.run_simple(netpdata, int(portdata), main)
    except Exception as expt:
        click.echo(" * " + click.style("Error occurred    : " + str(expt), fg="red"))


if __name__ == "__main__":
    mainfunc()
