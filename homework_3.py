import MySQLdb
from flask import request, redirect, url_for
from flask import Flask, render_template
from domain_model import TeamDomainModel,MatchDomainModel, PlayerDomainModel
from flask.views import View

app = Flask(__name__)


conn = MySQLdb.connect(host="localhost",user="root",
                  passwd="1234",db="football")


class IndexView(View):
    def dispatch_request(self):
        return render_template('index.html')


class ProcessMenu(View):

    def dispatch_request(self):
        action = request.args.get('action')
        if action == 'club':
            return redirect(url_for('ClubList'))

class ClubList(View):

    def dispatch_request(self):
        return render_template(
            'club.html', clubs=TeamDomainModel.get_all_teams())


class CreateClub(View):

    def dispatch_request(self):
        if (request.method == 'GET' or
                not request.form.get('name') or
                not request.form.get('city')):
            return render_template('create_team.html')
        else:
            td = TeamDomainModel.create_team(name=request.form.get('name'), city=request.form.get('city'))
            return redirect(url_for('ClubPage') + '?id=' + str(td.team_data._id) + '&create=True')


class ClubPage(View):

    def dispatch_request(self):
        if (request.method == 'GET' or
                not request.form.get('name') or
                not request.form.get('city')):

            club_id = request.args.get('id')
            create = request.args.get('create', False)
            return render_template('club_page.html', club=TeamDomainModel.get_team(club_id), create=create)
        else:
            club_id = request.args.get('id')
            td = TeamDomainModel.get_team(club_id)
            td.update_team(name=request.form.get('name'), city=request.form.get('city'))
            return render_template('club_page.html', club=td, update=True)


app.add_url_rule('/', view_func=IndexView.as_view('Index'), methods=['GET'])
app.add_url_rule('/process_menu', view_func=ProcessMenu.as_view('ProcessMenu'), methods=['GET'])
app.add_url_rule('/club_list', view_func=ClubList.as_view('ClubList'), methods=['GET'])
app.add_url_rule('/create_club', view_func=CreateClub.as_view('CreateClub'), methods=['GET', 'POST'])
app.add_url_rule('/club_page', view_func=ClubPage.as_view('ClubPage'), methods=['GET', 'POST'])



if __name__ == '__main__':
    app.run()
