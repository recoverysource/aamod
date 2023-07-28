#!/usr/bin/env python3
'''
Generate pages and content from meeting data.

This is for automation and testing; do not check generated files into git.
'''
import geopy
import glob
import json
import os
import pathlib
import subprocess
import time
import yaml


# Meeting "types" that get displayed in summaries
SUMMARY_TAGS = {
        'X': '<img src="/img/wheelchair.png" alt="Wheelchair Accessible" width="15" />',
        'BA': '<img src="/img/childcare.png" alt="Childcare Available" width="15" />',
        'O': 'Open',
        'B': 'Big Book',
        '12x12': '12x12',
        'TR': 'Traditions',
        'W': 'Women-Only',
        'G': 'Gay-Friendly',
        }


# use with: time.strftime('%d %b %Y', LAST_UPDATED)
LAST_UPDATED = time.localtime(int(subprocess.check_output(['git', 'log', '-1', '--pretty=%ct', 'data/*meetings*']).decode().strip()))


def main():
    '''
    Build site data
    '''
    meetings = load_yaml()

    # See "Path:" in function for files produced
    gen_meeting_times(meetings)
    gen_meeting_zips(meetings)
    gen_meeting_stubs(meetings)
    gen_meeting_json(meetings)
    gen_meeting_geos(meetings)  # if not present
    if gen_meeting_tex(meetings):
        gen_meeting_pdf(meetings)


def load_yaml(fpath='data/meetings.yaml'):
    '''
    Returns an object from a yaml file (or directory of yaml files)
    '''
    fpath = fpath.rstrip('/')
    # if fpath is a file
    if os.path.isfile(fpath):
        return yaml.load(open(fpath, 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
    # if fpath is a directory when .yaml is removed
    if not os.path.isdir(fpath) and os.path.isdir(fpath.rstrip('.yaml')):
        fpath = fpath.rstrip('.yaml')
    # if fpath a directory
    if os.path.isdir(fpath):
        m = {}
        for path in glob.glob(f'{fpath}/*'):
            tag = path.replace(f'{fpath}/', '', 1).replace('.yaml', '')
            m[tag] = yaml.load(open(path, 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
        return m
    raise Exception('Could not load yaml data')



def get_geo(address):
    '''
    Returns a geo object from a searched address
    '''
    locator = geopy.Nominatim(user_agent="aamod")
    return locator.geocode(address)


def gen_meeting_times(meetings):
    '''
    Generate a markdown file with list of all meeting times

    Path: content/meeting-times.md
    '''
    sorter = []
    for key, meeting in meetings.items():
        for day, hours in meeting['time'].items():
            for hour in hours:
                sorter.append(f'{day}#{hour}#{key}')
    sorter = sorted(sorter)

    with open('content/meeting-times.md', 'w', encoding='utf-8') as fh:
        fh.writelines([
            '---\n',
            'title: Meeting Times\n',
            'date: ', time.strftime('%Y-%m-%d', LAST_UPDATED), '\n',
            'layout: singlemap\n',
            'menu:\n',
            '  main:\n',
            '    weight: 30\n',
            '---\n\n',
            '<script language="javascript" type="text/javascript" src="/js/tconvert.js"></script>\n',
            '<b>Last Updated:</b> ', time.strftime('%d %b %Y', LAST_UPDATED), '\n\n',
            'Click the name of a meeting for additional information.',
            '<br />All meetings are non-smoking and closed, unless noted as Open.\n\n',
            ])
        for dow in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            fh.writelines([dow, '\n----\n\n'])
            for [day, hour, key] in [x.split('#') for x in sorter if x.startswith(dow)]:
                mtype = meetings[key].get('type', [])
                fh.writelines([
                    f'- <script lang="javascript"> document.write(tConvert("{hour}"));</script>',
                    f'<noscript>{hour}</noscript>',
                    f': <a href="/meetings/{key}">{meetings[key]["name"]}</a>',
                    f', {meetings[key].get("address", "").partition(",")[-1]}',
                    ' | ' if [k for k in SUMMARY_TAGS.keys() if k in mtype] else '',
                    ', '.join([v for k, v in SUMMARY_TAGS.items() if k in mtype]),
                    '\n',
                    ])
            fh.write('\n')


def gen_meeting_zips(meetings):
    '''
    Generate a markdown file of meetings based on location

    Path: content/meeting-zips.md
    '''
    sorter = []
    for key, meeting in meetings.items():
        sorter.append(f'{meeting["address"].split(",")[-1:]}#{key}')
    sorter = sorted(sorter)

    with open('content/meeting-zips.md', 'w', encoding='utf-8') as fh:
        fh.writelines([
            '---\n',
            'title: Locations\n',
            'date: ', time.strftime('%Y-%m-%d', LAST_UPDATED), '\n',
            'layout: singlemap\n',
            'menu:\n',
            '  main:\n',
            '    weight: 35\n',
            '---\n\n',
            '<b>Last Updated:</b> ', time.strftime('%d %b %Y', LAST_UPDATED), '\n\n',
            'Click the name of a meeting for additional information.',
            '<br />All meetings are non-smoking and closed, unless noted as Open.\n\n',
            ])
        z = -1
        for [zipcode, key] in [x.split('#') for x in sorter]:
            if z != zipcode:
                z = zipcode
                fh.writelines([
                    '\n',
                    meetings[key]['address'].partition(',')[-1],
                    '\n----\n\n',
                    ])
            mtype = meetings[key].get('type', [])
            fh.writelines([
                f'- <a href="/meetings/{key}">{meetings[key]["name"]}</a>',
                ', ', meetings[key].get("address", "").split(",")[0],
                ' | ' if [k for k in SUMMARY_TAGS.keys() if k in mtype] else '',
                ', '.join([v for k, v in SUMMARY_TAGS.items() if k in mtype]),
                '\n',
                ])
        fh.write('\n')


def gen_meeting_json(meetings):
    '''
    Generate a json file with list of all meeting times
    Format: https://github.com/code4recovery/spec

    Path: static/meeting-times.json
    '''
    conf = load_yaml('config.yaml')
    meeting_data = []
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for key, meeting in meetings.items():
        if 'json' in meeting.get('hidefrom', []):
            continue
        address = meeting.get('address').split(',')
        for dow, hours in meeting['time'].items():
            for hour in hours:
                meeting_data.append({
                    'name': meeting['name'],
                    'slug': f'{key}-{dow}-{hour}',
                    'day': days.index(dow),
                    'time': hour,
                    'timezone': 'America/Chicago',
                    'location': meeting.get('place', ''),
                    'notes': meeting.get('note', ''),
                    'region': conf.get('title'),
                    'url': f'{conf.get("baseURL").rstrip("/")}/meetings/{key}',
                    'types': meeting.get('type', []),
                    'approximate': False,
                    'address': address[0].strip(),
                    'city': address[1].strip(),
                    'state': address[2].strip(),
                    'postal_code': address[3].strip(),
                    'country': 'US',
                    })

    with open('static/meeting-times.json', 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(meeting_data, indent=4))


def gen_meeting_geos(meetings):
    '''
    Generate a yaml file with list of all meeting locations

    Path: data/geos.yaml
    '''
    if os.path.exists('data/geos.yaml'):
        print('WARN: data/geos.yaml exists, not re-creating')
        return

    locator = geopy.Nominatim(user_agent='aamod')
    with open('data/geos.yaml', 'w', encoding='utf-8') as fh:
        for key, meeting in meetings.items():
            if 'map' in meeting.get('hidefrom', []):
                continue
            if not meeting.get('address'):
                continue
            if not meeting.get('longitude') or not meeting.get('latitude'):
                location = locator.geocode(meeting['address'])
                if not location:
                    print(f'WARN: No geo data found for address: {meeting["address"]}')
                    continue
                if not meeting.get('longitude'):
                    meeting['longitude'] = location.longitude
                if not meeting.get('latitude'):
                    meeting['latitude'] = location.latitude
            fh.writelines([
                f'{key}:\n',
                f'  dsc: <b>{meeting.get("name", "")}</b>',
                f'<br>{meeting.get("address", "")}<br>',
                f'<a class="maplink" href="/meetings/{key}">Meeting Info</a>\n',
                f'  name: {meeting.get("name", "")}\n',
                f'  lng: {meeting.get("longitude", "-0.0")}\n',
                f'  lat: {meeting.get("latitude", "-0.0")}\n',
                '\n'])
            time.sleep(0.2)

def gen_meeting_stubs(meetings):
    '''
    Generate page stubs from data. These stubs use the [meeting-location] to
    offload templating logic to hugo's templating engine.
    meeting-location: themes/aamod/layouts/_default/meeting-location.html

    Path: content/meetings/*.md
    '''
    # Ensure directory exists
    pathlib.Path('content/meetings').mkdir(parents=True, exist_ok=True)

    # cleanup
    for path in glob.glob('content/meetings/*.md'):
        if path != 'content/meetings/_index.md':
            os.remove(path)

    for key, meeting in meetings.items():
        mtype = meeting.get('type', [])
        with open(f'content/meetings/{key}.md', 'w', encoding='utf-8') as fh:
            fh.writelines([
                '---\n',
                f'title: {meeting["name"]}\n',
                'layout: meeting-location\n',
                '---\n\n',
                ', '.join([SUMMARY_TAGS[x] for x in SUMMARY_TAGS if x in mtype]),
                '\n\n<!--more-->\n',
                ])


def _meeting_hours(hours):
    '''
    Prints a formatted list of meeting hours cast to 12-hour format.
    '''
    hrs = []
    for hour in sorted(hours):
        t = time.strftime('%-I:%M%p', time.strptime(hour, '%H:%M'))
        hrs.append(f'\\mbox{{{t}}}')
    return ', '.join(hrs)


def _meeting_tags(taglist):
    '''
    Prints a formatted list of (presented) meeting tags
    '''
    meeting_tags = []
    if 'X' in taglist:
        meeting_tags.append('WA')
    if 'O' in taglist:
        meeting_tags.append('Open')
    if meeting_tags:
        return r'\hfill ' + ', '.join(meeting_tags)
    return ''


def gen_meeting_tex(meetings):
    '''
    This generates the file used to produce the meetings list pdf.

    Path: static/meeting-schedule.tex
    '''
    conf = load_yaml('config.yaml')
    if not conf.get('pdf-blurbs'):
        return False

    meetings_sorter = []
    alanon_sorter = []
    for key, meeting in meetings.items():
        for day, hours in meeting['time'].items():
            min_hour = sorted(hours)[0]
            if 'AL-AN' in meetings[key]['type']:
                alanon_sorter.append(f'{day}#{min_hour}#{key}')
            else:
                meetings_sorter.append(f'{day}#{min_hour}#{key}')
    meetings_sorter = sorted(meetings_sorter)
    alanon_sorter = sorted(alanon_sorter)

    with open('static/meeting-schedule.tex', 'w', encoding='utf-8') as fh:

        anonlist = conf.get('pdf-cols', {}).get('anonlist', 2) > 0
        # Write document header and cover page
        fh.writelines([
            r'\documentclass[11pt,twoside,letterpaper]{article}', '\n',
            r'\usepackage[utf8]{inputenc}', '\n',
            r'\usepackage[letterpaper,margin=0.25in]{geometry}', '\n',
            r'\setlength{\parindent}{0em}', '\n',
            r'\setlength{\parskip}{1ex}', '\n',
            r'\usepackage{anyfontsize}', '\n',
            r'\usepackage{mathptmx}', '\n',
            r'\usepackage{multicol}', '\n',
            r'\usepackage{microtype}', '\n',
            r'\usepackage{graphicx}', '\n',
            r'\usepackage{enumitem}', '\n\n',
            r'\def\6pt{\fontsize{6}{7.2}\selectfont}', '\n',
            r'\def\7pt{\fontsize{7}{8}\selectfont}', '\n',
            r'\def\8pt{\fontsize{8.5}{10}\selectfont}', '\n',
            r'\def\gutter{\hspace{0.02\textwidth}}', '\n\n',
            r'\fontfamily{phv}\fontseries{mc}\selectfont', '\n',
            r'\begin{document}', '\n\n',
            r'  %%%%%%%%%', '\n',
            r'  % Cover %', '\n',
            r'  %%%%%%%%%', '\n\n',
            r'  % Front', '\n',
            r'  \rotatebox{180}{\begin{minipage}[l][\dimexpr.485\textheight]',
            r'[t]{\dimexpr 0.470\textwidth}', '\n',
            r'    {\center{\huge\textbf{', '\n',
            f'    {conf.get("title")}\\\\\n',
            r'    Alcoholics Anonymous\\', '\n',
            r'    Meeting Schedule}}', '\n\n',
            r'    \vskip 2ex', '\n',
            r'    \includegraphics[width=32ex, height=32ex]{themes/aamod/static/img/AAlogo.jpg}', '\n\n',
            r'    \vskip 1.5ex{\textbf{',
            conf.get('baseURL').split('/')[2], '}}\n',
            conf.get('pdf-blurbs', {}).get('front'), '\n',
            r'    \vskip 2ex{\large\textbf{24-Hour Helpline: ',
            conf['Params'].get('phone', '1-800-662-4357'), '}}\n',
            r'    \vskip 1ex{\footnotesize{',
            r'    Last Updated: ', time.strftime('%d %b %Y', LAST_UPDATED), '}}\n\n',
            r'    }', '\n',
            r'  \end{minipage}', '\n',
            r'  }\hfill', '\n',
            r'  % Folded: Back', '\n',
            r'  \rotatebox{180}{\begin{minipage}[r][\dimexpr 0.485\textheight]',
            r'[t]{\dimexpr 0.485\textwidth}', '\n',
            r'    % Note Space', '\n',
            r'    \begin{minipage}[l][\dimexpr.485\textheight]',
            r'[t]{\dimexpr 0.485\textwidth}', '\n',
            r'      {\8pt\textbf{Notes and Phone Numbers}}\hrulefill', '\n\n',
            r'      {\6pt', '\n',
            ])
        for _ in range(24):
            fh.writelines([r'      \hphantom{.}\hrulefill\\', '\n'])
        fh.writelines([
            r'      .\hrulefill', '\n',
            r'      }', '\n',
            r'    \end{minipage}', '\n',
            r'    \gutter', '\n',
            r'    \begin{minipage}[r][\dimexpr 0.485\textheight]',
            r'[t]{\dimexpr 0.485\textwidth}', '\n',
            r'      {\8pt\textbf{Additional Meeting Information}}\hrulefill', '\n\n',
            conf.get('pdf-blurbs', {}).get('resources'), '\n\n',
            r'      \vskip 2ex', '\n',
            r'      {\8pt\textbf{AA Preamble}}\hrulefill\vskip 1ex', '\n\n',
            r'      {\8pt', '\n',
            r'      Alcoholics Anonymous is a fellowship of men and women ',
            r'who share their experience, strength and hope with each other that ',
            r'they may solve their common problem and help', '\n',
            r'      others to recover from alcoholism.\\', '\n\n',
            r'      The only requirement for membership is a desire to stop ',
            r'drinking. There are no dues or fees for AA membership; we are ',
            r'self-supporting through our own contributions.\\', '\n\n',
            r'      A.A. is not allied with any sect, denomination, politics, ',
            r'organization or institution; does not wish to engage in any ',
            r'controversy; neither endorses nor opposes any causes.\\', '\n\n',
            r'      Our primary purpose is to stay sober and help other ',
            r'alcoholics to achieve sobriety.\\', '\n\n',
            r'      \6pt{\copyright The A.A. Grapevine, Inc.}', '\n\n',
            r'      }', '\n',
            r'    \end{minipage}', '\n',
            r'  \end{minipage}', '\n',
            r'  }\vfill', '\n',
            r'  % Folded: Inside-Left', '\n',
            r'  \begin{minipage}[l][\dimexpr 0.485\textheight]',
            r'[t]{\dimexpr 0.485\textwidth}', '\n',
            r'    % Twelve Steps', '\n',
            r'    \begin{minipage}[l][\dimexpr.485\textheight]',
            r'[t]{\dimexpr 0.445\textwidth}', '\n',
            r'      \raggedright', '\n',
            r'      {\8pt\textbf{The 12 Steps of AA}}\hrulefill', '\n\n',
            r'      {\7pt', '\n',
            r'      \begin{enumerate}[leftmargin=4ex]', '\n',
            r'        \itemsep 0em', '\n',
            r'        \item We admitted that we were powerless over alcohol--',
            r'that our lives had become unmanageable.', '\n',
            r'        \item Came to believe that a power greater than ',
            r'ourselves could restore us to sanity.', '\n',
            r'        \item Made a decision to turn our will and our lives ',
            r'over to the care of God as we understood Him.', '\n',
            r'        \item Made a searching and fearless moral inventory of ',
            r'ourselves.', '\n',
            r'        \item Admitted to God, to ourselves, and to another ',
            r'human being the exact nature of our wrongs.', '\n',
            r'        \item Were entirely ready to have God remove all these ',
            r'defects of character.', '\n',
            r'        \item Humbly asked Him to remove our shortcomings.', '\n',
            r'        \item Made a list of all the persons we had harmed, and ',
            r'became willing to make amends to them all.', '\n',
            r'        \item Made direct amends to such people wherever ',
            r'possible, except when to do so would injure them or others.', '\n',
            r'        \item Continued to take personal inventory and when we ',
            r'were wrong promptly admitted it.', '\n',
            r'        \item Sought through prayer and meditation to improve ',
            r'our conscious contact with God as we understood Him, praying ',
            r'only for the knowledge of His will for us and the power to ',
            r'carry that out.', '\n',
            r'        \item Having had a spiritual awakening as the result ',
            r'of these steps, we tried to carry this message to alcoholics, ',
            r'and to practice these principles in all our affairs.', '\n',
            r'      \end{enumerate}', '\n',
            r'      }', '\n',
            r'    \end{minipage}', '\n',
            r'    \gutter', '\n',
            r'    % Twelve Traditions', '\n',
            r'    \begin{minipage}[r][\dimexpr 0.485\textheight]',
            r'[t]{\dimexpr 0.525\textwidth}', '\n',
            r'      \raggedright', '\n',
            r'      {\8pt\textbf{The Twelve Traditions}}\hrulefill', '\n\n',
            r'      {\7pt', '\n',
            r'      \begin{enumerate}[leftmargin=4ex]', '\n',
            r'        \itemsep 0em', '\n',
            r'        \item Our common welfare should come first; personal ',
            r'recovery depends upon A.A. unity.', '\n',
            r'        \item For our group purpose there is but one ultimate ',
            r'authority--a loving God as He may express Himself in our ',
            r'group conscience. Our leaders are but trusted servants; they ',
            r'do not govern.', '\n',
            r'        \item The only requirement for A.A. membership is a ',
            r'desire to stop drinking.', '\n',
            r'        \item Each group should be autonomous except in matters ',
            r'affecting other groups or A.A. as a whole.', '\n',
            r'        \item Each group has but one primary purpose--to ',
            r'carry its message to the alcoholic who still suffers.', '\n',
            r'        \item An A.A. group ought never endorse, finance, or ',
            r'lend the A.A. name to any related facility or outside ',
            r'enterprise, lest problems of money, property, and prestige ',
            r'divert us from our primary purpose.', '\n',
            r'        \item Every A.A. group ought to be fully self-supporting, ',
            r'declining outside contributions.', '\n',
            r'        \item Alcoholics Anonymous should remain forever ',
            r'nonprofessional, but our service centers may employ special ',
            r'workers.', '\n',
            r'        \item A.A. as such, ought never be organized; but we ',
            r'may create service boards or committees directly responsible ',
            r'to those they serve.', '\n',
            r'        \item Alcoholics Anonymous has no opinion on outside ',
            r'issues; hence the A.A. name ought never be drawn into public ',
            r'controversy.', '\n',
            r'        \item Our public relations policy is based on ',
            r'attraction rather than promotion; we need always maintain ',
            r'personal anonymity at the level of press, radio and films.', '\n',
            r'        \item Anonymity is the spiritual foundation of all our ',
            r'traditions, ever reminding us to place principles before ',
            r'personalities.', '\n',
            r'      \end{enumerate}', '\n',
            r'      }', '\n',
            r'    \end{minipage}', '\n',
            r'  \end{minipage}', '\n',
            r'  \hfill', '\n',
            r'  % Folded: Inside-Right', '\n',
            r'  \begin{minipage}[r][\dimexpr 0.485\textheight][t]{\dimexpr 0.485\textwidth}', '\n',
            ])
        if anonlist:
            fh.writelines([
                r'    {\textbf{Al-Anon}}\hrulefill\\', '\n',
                conf.get('pdf-blurbs', {}).get('alanon'), '\n\n',
                r'    \begin{multicols}{',
                str(conf.get('pdf-cols', {}).get('anonlist', 2)), '}\n',
                ])

            # Write alanon items
            for i, dow in enumerate(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']):
                if i == 0:
                    fh.write('    ')
                fh.writelines([
                    r'\vskip 2ex{\8pt\textbf{', dow.upper(), r'}}\hrulefill\vskip 1ex', '\n\n',
                    r'    {\7pt', '\n',
                    ])
    
                for [day, hour, key] in [x.split('#') for x in alanon_sorter if x.startswith(dow)]:
                    if 'pdf' in meetings[key].get('hidefrom', []):
                        continue
                    meeting_tags = _meeting_tags(meetings[key]['type'])
                    fh.writelines([
                        r'    \begin{minipage}{\columnwidth}', '\n',
                        r'    \vskip 1ex\textbf{',
                        meetings[key]['name'],
                        r'\hfill\begin{minipage}{\dimexpr\linewidth-',
                        str(len(meetings[key]['name']) + 3),
                        r'ex\relax}\raggedleft ',
                        _meeting_hours(meetings[key]['time'][dow]),
                        r'\end{minipage}}\\', '\n',
                        ])
                    if meetings[key].get('place'):
                        fh.writelines(['    ', meetings[key]['place'], meeting_tags, r'\\', '\n'])
                    fh.writelines([
                        '    ',
                        ','.join(meetings[key]['address'].split(',', 2)[:2])
                        ])
                    if not meetings[key].get('place'):
                        fh.write(meeting_tags)
                    if not meetings[key].get('note'):
                        fh.writelines([
                            '\n', r'    \end{minipage}', '\n\n',
                            ])
                    else:
                        fh.writelines([
                            '\\\\\n    ', r'{\6pt',
                            '\n    ', meetings[key]['note'].split('\n')[0], '}\n',
                            r'    \end{minipage}', '\n\n',
                            ])
                fh.write('    }')

            # write alanon footer and resume cover
            fh.writelines([
                r'    \end{multicols}', '\n',
                r'  \end{minipage}', '\n\n',
                r'  \pagebreak', '\n\n',
                ])
            # ^ if anonlist ^

        # Write meeting list header
        fh.writelines([
            r'  %%%%%%%%%%%%%%%%', '\n',
            r'  % Meeting List %', '\n',
            r'  %%%%%%%%%%%%%%%%', '\n\n',
            r'    {\textbf{AA Meetings}}\hrulefill', '\n\n',
            r'  \begin{multicols}{',
            str(conf.get('pdf-cols', {}).get('aalist', 4)), '}\n\n',
            ])

        # Write meeting list
        for i, dow in enumerate(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']):
            if i == 0:
                fh.write('    ')
            fh.writelines([
                r'\vskip 2ex{\8pt\textbf{', dow.upper(), r'}}\hrulefill\vskip 1ex', '\n\n',
                r'    {\7pt', '\n',
                ])

            for [day, hour, key] in [x.split('#') for x in meetings_sorter if x.startswith(dow)]:
                if 'pdf' in meetings[key].get('hidefrom', []):
                    continue
                meeting_tags = _meeting_tags(meetings[key]['type'])
                fh.writelines([
                    r'    \begin{minipage}{\columnwidth}', '\n',
                    r'    \vskip 1ex\textbf{',
                    meetings[key]['name'],
                    r'\hfill\begin{minipage}{\dimexpr\linewidth-',
                    str(len(meetings[key]['name']) + 3),
                    r'ex\relax}\raggedleft ',
                    _meeting_hours(meetings[key]['time'][dow]),
                    r'\end{minipage}}\\', '\n',
                    ])
                if meetings[key].get('place'):
                    fh.writelines(['    ', meetings[key]['place'], meeting_tags, r'\\', '\n'])
                fh.writelines([
                    '    ',
                    ','.join(meetings[key]['address'].split(',', 2)[:2])
                    ])
                if not meetings[key].get('place'):
                    fh.write(meeting_tags)
                if not meetings[key].get('note'):
                    fh.writelines([
                        '\n', r'    \end{minipage}', '\n\n',
                        ])
                else:
                    fh.writelines([
                        '\\\\\n    ', r'{\6pt',
                        '\n    ', meetings[key]['note'].split('\n')[0], '}\n',
                        r'    \end{minipage}', '\n\n',
                        ])
            fh.write('    }')

        # Write meeting list footer
        fh.writelines([
            '\n', r'    \vskip 5ex{\8pt\textbf{DETAILS}}\hrulefill\vskip 1ex', '\n\n',
            r'    {\8pt', '\n',
            r'    All meetings are non-smoking and Closed, unless noted as Open.', '\n\n',
            r'    \textbf{Open}: Anyone interested in AA\\ ', '\n',
            r'    \textbf{Closed}: Limited to those who have\\',
            r'\hphantom{.}\hskip 7ex a desire to stop drinking\\', '\n',
            r'    \textbf{WA}: Wheelchair Accessible', '\n\n',
            r'    {\7pt\textbf{Current:} ', conf.get('baseURL'), r'meeting-times}\\', '\n',
            r'    {\7pt\textbf{Events:} ', conf.get('baseURL'), r'events}\\', '\n\n',
            r'    \vskip 2ex\framebox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{\itshape{\7pt', '\n',
            conf.get('pdf-blurbs', {}).get('details'), '}} }\n\n',
            r'    }', '\n\n',
            ])

        if not anonlist:
            fh.write(r'  \end{multicols}\end{minipage}\end{document}')
        else:
            fh.write(r'  \end{multicols}\end{document}')
    return True


def gen_meeting_pdf(meetings):
    '''
    Generate PDF using LaTeX and templates

    Path: static/meeting-schedule.pdf
    '''
    os.system('pdflatex ./static/meeting-schedule.tex >/dev/null')
    os.rename('./meeting-schedule.pdf', './static/meeting-schedule.pdf')


if __name__ == '__main__':
    main()
