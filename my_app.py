import time

from celery import Celery

from flask import Flask, jsonify, render_template, request, url_for


app = Flask(__name__)
app.vars = {}
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/main', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        return render_template('main.html')
    else:  # request was a POST
        num_questions = int(request.form['num_questions'])
        app.vars['num_questions'] = num_questions
        print(app.vars)
        return render_template('main.html')


@app.route('/longtask', methods=['POST'])
def do_computation():
    # set num questions, could return a 400 here and send error
    # message to client as well
    if request.form["num_questions"] == "":
        num_questions = 1
    else:
        num_questions = int(request.form["num_questions"])

    app.vars['num_questions'] = num_questions

    task = long_task.apply_async(args=[{'num_questions': num_questions}])
    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}


@celery.task(bind=True)
def long_task(self, args):
    """Background task that runs a long function with progress reports."""
    self.update_state(state='PROGRESS', meta={'state': 0})
    time.sleep(5)
    self.update_state(state='PROGRESS2', meta={'state': 1})
    filename = '{}.txt'.format(args['num_questions'])
    with open(filename, 'w') as f:
        f.write('Blah')
    time.sleep(5)
    self.update_state(state='PROGRESS3', meta={'state': 2})
    return {'state': 2, 'result': True}


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    state = task.info.get('state', '')
    if state == 0:
        status = 'Calculation has yet to start'
    elif state == 1:
        status = 'Calculation is in progress'
    elif state == 2:
        status = 'Calculation complete'
    else:
        status = 'Something weird happened'
    response = {'status': status, 'state': state}
    try:
        response['result'] = task.info['result']
    except:
        pass
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
