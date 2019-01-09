import os
import re

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
)


USPS_INTL_RE = re.compile(r'[A-Z]{2}\d{9}[A-Z]{2}')

DHL = 'http://www.dhl.com/en/express/tracking.html?AWB={}'
FEDEX = 'https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber={}'
UPS = 'https://www.ups.com/track?loc=en_US&tracknum={}'
USPS = 'https://tools.usps.com/go/TrackConfirmAction?tLabels={}'


app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=os.urandom(12))


@app.route('/', methods=['POST', 'GET'])
def front():
    if request.method == 'POST':
        num = request.form.get('num')
        carrier = request.form.get('carrier')
        if num is None or carrier is None:
            flash('Both carrier and number are required', 'error')
            return render_template('front.html')
        url = 'https://trck.ai/{}/{}'.format(carrier, num)
        message = 'Your short-URL is <a href="{0}">{0}</a>'.format(url)
        if _is_ups(num) or _is_fedex(num) or _is_usps(num):
            url = 'https://trck.ai/{}'.format(num)
            message += (' - however, we can probably guess it, so you can '
                        'just use <a href="{0}">{0}</a>').format(url)
        flash(message, 'success')
    return render_template('front.html')


@app.route('/dhl/<num>')
def dhl(num):
    return redirect(DHL.format(num))


@app.route('/fedex/<num>')
def fedex(num):
    return redirect(FEDEX.format(num))


@app.route('/ups/<num>')
def ups(num):
    return redirect(UPS.format(num))


@app.route('/usps/<num>')
def usps(num):
    return redirect(USPS.format(num))


@app.route('/<num>')
def guess(num):
    if _is_ups(num):
        return redirect(UPS.format(num))
    if _is_fedex(num):
        return redirect(FEDEX.format(num))
    if _is_usps(num):
        return redirect(USPS.format(num))
    # Default to DHL ¯\_(ツ)_/¯
    return redirect(DHL.format(num))


def _is_fedex(num):
    try:
        _ = int(num)
        return len(num) in (12, 15)
    except ValueError:
        return False


def _is_ups(num):
    return num[:2] == '1Z'


def _is_usps(num):
    try:
        _ = int(num)
        return len(num) == 22
    except ValueError:
        return USPS_INTL_RE.match(num)
