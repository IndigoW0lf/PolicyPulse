from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Legislation

@app.route('/add-legislation', methods=['POST'])
def add_legislation():
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        # ... (get other fields similarly)
        
        new_legislation = Legislation(title=title, summary=summary, ...)
        db.session.add(new_legislation)
        db.session.commit()
        return "Legislation added successfully!"
    
@app.route('/legislations')
def get_legislations():
  legislations = Legislation.query.all()
  return render_template('legislations.html' legislations=legislations)

@app.route('/edit-legislation/<int:id>', methods=['GET', 'POST'])
def edit_legislation(id):
    legislation = Legislation.query.get(id)
    if request.method == 'POST':
        legislation.title = request.form['title']
        legislation.summary = request.form['summary']
        # ... (update other fields similarly)
        
        db.session.commit()
        return "Legislation updated successfully!"
    return render_template('edit_legislation.html', legislation=legislation)

@app.route('/delete-legislation/<int:id>', methods=['POST'])
def delete_legislation(id):
    legislation = Legislation.query.get(id)
    db.session.delete(legislation)
    db.session.commit()
    return "Legislation deleted successfully!"