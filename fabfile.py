
from fabric.api import local

def prepare_deploy():
	## Commit changes to master branch
	local("git add -A")
	local("git commit -m 'commit with fabric'")
	local("git push origin master")

	## Prepare to push heroku branch with different admin password
	local("git checkout heroku")
	local("git rebase master")
	local("git push -f heroku heroku:master")

	## Checkout master branch again
	local("git checkout master")