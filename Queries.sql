-- What openings do specific players play the most?
SELECT White_Name, Opening, COUNT(*) AS PlayCount
FROM `match`
WHERE White_Name = 'Specific Player'
GROUP BY `match`.Opening
ORDER BY PlayCount DESC
LIMIT 10;

SELECT Black_Name, Opening, COUNT(*) AS PlayCount
FROM `match`
WHERE Black_Name = 'Specific Player'
GROUP BY `match`.Opening
ORDER BY PlayCount DESC
LIMIT 10;


-- What are the most commonly played openings?
SELECT opening.Name, COUNT(`match`.Opening) AS PlayCount
FROM `match`
INNER JOIN opening ON `match`.Opening = opening.FEN
GROUP BY opening.Name
ORDER BY PlayCount DESC
LIMIT 10;


-- What openings have books?
SELECT opening.Name AS OpeningName, book.Title as BookTitle
FROM book_opening
INNER JOIN opening ON book_opening.Opening_FEN = opening.FEN
INNER JOIN book ON book_opening.Book_Title = book.Title;


-- What is a player's win rate with a specific opening?
SELECT SUM(Result = '1-0' AND White_Name = 'Specific Player') / COUNT(*) * 100.0 AS WinRate
FROM `match`
WHERE (White_Name = 'Specific Player' AND Opening = 'Specific Opening');

SELECT SUM(Result = '0-1' AND Black_Name = 'Specific Player') / COUNT(*) * 100.0 AS WinRate
FROM `match`
WHERE (Black_Name = 'Specific Player' AND Opening = 'Specific Opening');


-- How wide is the win rate between when a player plays black or white?
SELECT White_Name AS Player, (SUM(CASE WHEN Result = '1-0' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS WhiteWinRate,
	   (SUM(CASE WHEN Result = '1/2' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS DrawRate,
       (SUM(CASE WHEN Result = '0-1' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS WhiteLossRate
FROM `match`
WHERE White_Name = 'Specific Player';

SELECT Black_Name AS Player, (SUM(CASE WHEN Result = '0-1' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS BlackWinRate,
	   (SUM(CASE WHEN Result = '1/2' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS DrawRate,
       (SUM(CASE WHEN Result = '1-0' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS BlackLossRate
FROM `match`
WHERE Black_Name = 'Specific Player';


-- What masters have published books?
SELECT DISTINCT master.Name, book.Title as PublishedBook
FROM book_master
INNER JOIN master ON book_master.Master_Name = master.Name
INNER JOIN book ON book_master.Book_Title = book.Title;


-- How many times has a player appeared in the top 100?
SELECT Player_Name, COUNT(*) AS Appearances
FROM yearlytop100
GROUP BY Player_Name
ORDER BY Appearances DESC;


-- When a match enters the endgame, how common is it for the result to be different from hypothetical best play?
SELECT match_endgame.Endgame_FEN, endgame.Result AS BestPlayResult, COUNT(*) AS TotalMatches,
       SUM(CASE WHEN `match`.Result = endgame.Result THEN 1 ELSE 0 END) / TotalMatches * 100.0 AS DifferenceRate
FROM match_endgame
INNER JOIN endgame ON match_endgame.Endgame_FEN = endgame.FEN
INNER JOIN `match` ON match_endgame.Match_Event = `match`.`Event`
				   AND match_endgame.Match_Round = `match`.Round
GROUP BY match_endgame.Endgame_FEN, endgame.Result
ORDER BY DifferenceRate DESC;