DELIMITER //

-- What openings do specific players play the most?
CREATE PROCEDURE WhitePlayerOpening(IN PlayerName VARCHAR(255))
BEGIN
	SELECT White_Name, Opening, COUNT(*) AS PlayCount
	FROM `match`
	WHERE White_Name = PlayerName
	GROUP BY `match`.Opening
	ORDER BY PlayCount DESC
	LIMIT 10
END;

CREATE PROCEDURE BlackPlayerOpening(IN PlayerName VARCHAR(255))
BEGIN
	SELECT Black_Name, Opening, COUNT(*) AS PlayCount
	FROM `match`
	WHERE Black_Name = PlayerName
	GROUP BY `match`.Opening
	ORDER BY PlayCount DESC
	LIMIT 10
END;



-- What is a player's win rate with a specific opening?
CREATE PROCEDURE WhitePlayerOpeningWins(IN PlayerName VARCHAR(255), OpeningName VARCHAR(255))
BEGIN
	SELECT SUM(Result = '1-0' AND White_Name = PlayerName) / COUNT(*) * 100.0 AS WinRate
	FROM `match`
	WHERE (White_Name = PlayerName AND Opening = OpeningName)
END;

CREATE PROCEDURE BlackPlayerOpeningWins(IN PlayerName VARCHAR(255), OpeningName VARCHAR(255))
BEGIN
	SELECT SUM(Result = '0-1' AND Black_Name = PlayerName) / COUNT(*) * 100.0 AS WinRate
	FROM `match`
	WHERE (Black_Name = PlayerName AND Opening = OpeningName)
END;



-- How wide is the win rate between when a player plays black or white?
CREATE PROCEDURE WhiteResults(IN PlayerName VARCHAR(255))
BEGIN
	SELECT White_Name AS Player, (SUM(CASE WHEN Result = '1-0' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS WhiteWinRate,
		   (SUM(CASE WHEN Result = '1/2' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS DrawRate,
		   (SUM(CASE WHEN Result = '0-1' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS WhiteLossRate
	FROM `match`
	WHERE White_Name = PlayerName
END;

CREATE PROCEDURE BlackResults(IN PlayerName VARCHAR(255))
BEGIN
SELECT Black_Name AS Player, (SUM(CASE WHEN Result = '0-1' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS BlackWinRate,
	   (SUM(CASE WHEN Result = '1/2' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS DrawRate,
       (SUM(CASE WHEN Result = '1-0' THEN 1 ELSE 0 END)) / COUNT(*) * 100 AS BlackLossRate
FROM `match`
WHERE Black_Name = PlayerName;
END;



-- Has a master published books?
CREATE PROCEDURE GetBooksByMaster(IN PlayerName VARCHAR(255))
BEGIN
	SELECT DISTINCT master.Name, book.Title as PublishedBook
	FROM book_master
	INNER JOIN master ON book_master.Master_Name = master.Name
	INNER JOIN book ON book_master.Book_Title = book.Title
	WHERE master.Name = PlayerName
END;



-- How many times has a player appeared in the top 100?
CREATE PROCEDURE Top100Appearances(IN PlayerName VARCHAR(255))
BEGIN
	SELECT Player_Name, COUNT(*) AS Appearances
	FROM yearlytop100
	WHERE Player_Name = PlayerName
	GROUP BY Player_Name
	ORDER BY Appearances DESC
END;

DELIMITER ;

-- When a match enters the endgame, how common is it for the result to be different from hypothetical best play?
SELECT 
    match_endgame.Endgame_FEN, 
    endgame.Result AS BestPlayResult, 
    COUNT(*) AS TotalMatches,
    SUM(CASE WHEN `match`.Result = endgame.Result THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DifferenceRate
FROM match_endgame
INNER JOIN endgame ON match_endgame.Endgame_FEN = endgame.FEN
INNER JOIN `match` ON match_endgame.Match_Event = `match`.`Event`
                   AND match_endgame.Match_Round = `match`.Round
GROUP BY match_endgame.Endgame_FEN, endgame.Result
ORDER BY DifferenceRate DESC;



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
