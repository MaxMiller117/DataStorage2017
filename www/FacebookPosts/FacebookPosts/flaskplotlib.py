from flask import Flask, make_response
app = Flask(__name__)

@app.route("/weekly_followers.png")
@app.route("/weekly_followers.png/<group>")
def weekly_followers(group="Blacktivists"):
    import datetime
    import StringIO
    import random

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    from matplotlib.axes import Axes
    import psycopg2


    conn = psycopg2.connect("dbname=fb_data user=njohnson")
    cur = conn.cursor()

    query = """CREATE OR REPLACE FUNCTION page_percent_change(parm1 text)
      RETURNS TABLE (year double precision, weekly double precision, percent_change numeric)
    AS
    $body$
      SELECT
        a.year,a.weekly, round(((cast(a.followers AS numeric) - cast(a.lag AS numeric))/ NULLIF(cast(a.lag AS numeric),0)) * 100,4) AS percent_change 
    FROM
    (
        SELECT *,lag(followers) OVER (partition BY name) AS lag FROM followers_weekly
    )
        AS a WHERE name = parm1;
    $body$
    language sql; """
    cur.execute(query)

    query = """
    select year, weekly, percent_change from page_percent_change('%s');""" % group

    cur.execute(query)

    data = cur.fetchall()
    
    # Calculate weeks from the first observation
    years, weeks, percent_changes = zip(*data)
	
    year0 = years[0]
    week0 = weeks[0]
	
    weeks_from_start = []
	
    for i in range(len(years)):
        weeks_from_start.append((years[i] - year0) * 52 + weeks[i] - week0)
	
    fig=Figure()
    ax=fig.add_subplot(111)
    ax.set_xlabel('Weeks From First Post')
    ax.set_ylabel('Percent Change in Followers')
    #ax.set_title()
    
    ax.plot(weeks_from_start, percent_changes)
    ax.set_title(group)
    #ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    #fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route("/activity_by_time_of_day.png/<group>")
def activity_by_time_of_day(group="Blacktivists"):
    import datetime
    import StringIO
    import random

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    from matplotlib.axes import Axes
    import psycopg2

    NUM_HOURS = 24 # avoiding magic numbers, maybe this code will one day run on other planets?

    conn = psycopg2.connect("dbname=fb_data user=njohnson")
    cur = conn.cursor()
    
    query = """SELECT time, interactions FROM posts WHERE page_id = (SELECT id FROM pages WHERE name = '%s');""" % group

    cur.execute(query)

    data = cur.fetchall()

    # Grab lists of data
    times, interactions = zip(*data)

    # Construct bins of total interactions across the hours each time occurs in (from 00 to 23)
    interactions_per_hour = dict.fromkeys(range(NUM_HOURS),0)
    for time in times:
        hour = int(time[:2])
        interactions_per_hour[hour] = interactions_per_hour.get(hour, 0) + 1

    fig=Figure()
    ax=fig.add_subplot(111)
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Interactions')

    ax.bar(interactions_per_hour.keys(), interactions_per_hour.values())
    ax.set_title(group)

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response



if __name__ == "__main__":
    app.run()
    #weekly_followers()
