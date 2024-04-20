#!/usr/bin/make -f
##
# A simple wrapper for common developer commands.
# Most common commands: [run, clean]
##

site/index.html: prebuild ../mainroad
	hugo --minify -d ../site \
		--source exampleSite/ --themesDir ../..

browse: site/index.html
	sensible-browser site/index.html

run: prebuild ../mainroad
	hugo server --disableFastRender \
		--source exampleSite/ --themesDir ../..

prebuild:
	cd exampleSite && python3 ../prebuild.py

# Exclusively for aamod-exampleSite
../mainroad:
	git clone https://github.com/Vimux/Mainroad.git ../mainroad
	git -C ../mainroad reset --hard ed54a7c

clean:
	# hugo
	$(RM) -r exampleSite/.hugo_build.lock exampleSite/site exampleSite/resources
	# prebuild
	find exampleSite/content/meetings ! -name '_index.md' -type f -exec rm {} +
	$(RM) exampleSite/static/meeting-schedule.tex exampleSite/static/meeting-schedule.pdf
	$(RM) exampleSite/meeting-schedule.aux exampleSite/meeting-schedule.log

.PHONY: browse prebuild clean
