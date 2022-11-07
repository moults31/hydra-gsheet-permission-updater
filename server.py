# SPDX-FileCopyrightText: 2022 Zac Moulton
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from flask import Flask
from waitress import serve

import update_permissions

app = Flask(__name__)

@app.route("/")
def index():
    update_permissions.main(delete=False)
    date = datetime.now()
    report = "Updated at {}".format(date)
    app.logger.info(report)
    return report


if __name__ == "__main__":
    print("Starting server")
    serve(app, host="0.0.0.0", port=8080)