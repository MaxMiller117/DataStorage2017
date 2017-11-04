from flask import Flask, make_response
app = Flask(__name__)

@app.route("/weekly_followers.png")
@app.route("/weekly_followers.png/<group>")
def weekly_followers(group="Blacktivist"):
    import datetime
    import StringIO
    import random

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    from matplotlib.axes import Axes
    import psycopg2


    conn = psycopg2.connect("dbname=fb_data user=srive326")
    cur = conn.cursor()

    query = """CREATE OR REPLACE FUNCTION source_percent_change(parm1 text)
      RETURNS TABLE (year double precision, weekly double precision, percent_change numeric)
    AS
    $body$
      SELECT
        a.year,a.weekly, round(((cast(a.followers AS numeric) - cast(a.lag AS numeric))/ NULLIF(cast(a.lag AS numeric),0)) * 100,4) AS percent_change 
    FROM
    (
        SELECT *,lag(followers) OVER (partition BY source) AS lag FROM followers_weekly
    )
        AS a WHERE source = parm1;
    $body$
    language sql; """
    cur.execute(query)

    query = """
    select year, weekly, percent_change from source_percent_change('%s')""" % group

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
    #ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    #fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


if __name__ == "__main__":
    app.run()
    #weekly_followers()
