-- Delete tables if they already exist. Easier than a bunch of IF NOT EXISTS
DROP TABLE IF EXISTS fb_data;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS pages CASCADE;
DROP TABLE IF EXISTS page_followers CASCADE;
DROP TABLE IF EXISTS followers_weekly CASCADE;

-- Create table to hold the unnormalized data
CREATE TABLE fb_data(
id varchar, 
source varchar, 
page_url varchar,
followers varchar,
"date" date, 
"time" time, 
time_zone varchar,
interactions varchar,
post_type varchar, 
post_message varchar, 
post_link varchar
);

-- load unnormalized data from csv
\copy fb_data from './facebook_pages_moved.csv' with CSV HEADER

-- Now start creating normalized tables

-- create pages table which simply describes all pages of interest that exist
CREATE TABLE pages(
id serial primary key,
name varchar,
url varchar);

INSERT INTO pages(name, url) SELECT reverse(split_part(reverse(page_url), '/', 1)), page_url FROM fb_data GROUP BY page_url;


-- create page_followers table to track followers for pages over time
CREATE TABLE page_followers(
page_id integer references pages(id),
followers integer,
"date" date,
"time" time,
time_zone varchar
);

INSERT INTO page_followers(page_id, followers, "date", "time", time_zone) SELECT p.id, fb.followers::integer, fb."date", fb."time", fb.time_zone FROM fb_data AS fb, pages AS p WHERE fb.page_url = p.url;


-- create posts table describing specific posts to various facebook pages
CREATE TABLE posts AS SELECT fb.id AS id, p.id AS page_id, "date", "time", time_zone, interactions, post_message, post_link FROM fb_data AS fb INNER JOIN pages AS p ON (fb.page_url = p.url);

--ALTER TABLE posts ADD COLUMN page_id integer; 
ALTER TABLE posts ADD CONSTRAINT fk_page_id FOREIGN KEY(page_id) REFERENCES pages(id);
--UPDATE posts SET page_id = pages.id FROM pages WHERE source = pages.name AND fb_data.page_url = pages.url;

ALTER TABLE posts ALTER COLUMN id SET DATA TYPE integer USING (id::integer);
ALTER TABLE posts ADD CONSTRAINT pk_id PRIMARY KEY(id);

--sql to make table with followers by week
CREATE TABLE followers_weekly AS SELECT name, max(followers) AS followers, date_part('year', "date"::date) AS year,
	date_part('week', "date"::date) AS weekly
	FROM page_followers INNER JOIN pages ON (page_followers.page_id = pages.id)
	GROUP BY name, year, weekly
	ORDER BY name, year, weekly;
