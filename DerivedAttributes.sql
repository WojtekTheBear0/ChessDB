UPDATE endgame
SET Type = CASE
    -- King vs Pawn
    WHEN FEN REGEXP '^[^rnbqkpRNBQKP]*[Pp][^rnbqkpRNBQKP]*$'
		AND LENGTH(REPLACE(FEN, ' ', '')) = 10 THEN 'King Pawn'
    
    -- Rook vs Minor Piece
    WHEN FEN REGEXP '^[^rnbqkpRNBQKP]*[R][^rnbqkpRNBQKP]*[nb][^rnbqkpRNBQKP]*$' OR FEN REGEXP '^[^rnbqkpRNBQKP]*[r][^rnbqkpRNBQKP]*[NB][^rnbqkpRNBQKP]*$'
		AND LENGTH(REPLACE(FEN, ' ', '')) = 10 THEN 'Rook v Minor'

    -- Rook pawn vs Rook 
    WHEN FEN REGEXP '^[^rnbqkpRNBQKP]*[R][^rnbqkpRNBQKP]*[rp][^rnbqkpRNBQKP]*$' OR FEN REGEXP '^[^rnbqkpRNBQKP]*[r][^rnbqkpRNBQKP]*[RP][^rnbqkpRNBQKP]*$'
		AND LENGTH(REPLACE(FEN, ' ', '')) = 10 THEN 'Rook Pawn v Rook' 

    -- Queen vs Rook
    WHEN FEN REGEXP '^[^rnbqkpRNBQKP]*[Q][^rnbqkpRNBQKP]*[r][^rnbqkpRNBQKP]*$' OR FEN REGEXP '^[^rnbqkpRNBQKP]*[q][^rnbqkpRNBQKP]*[R][^rnbqkpRNBQKP]*$'
		AND LENGTH(REPLACE(FEN, ' ', '')) = 10 THEN 'Queen v Rook'

    -- Pawns vs Minor
    WHEN FEN REGEXP '^[^rnbqkpRNBQKP]*[P]+[^rnbqkpRNBQKP]*[nb][^rnbqkpRNBQKP]*$' OR FEN REGEXP '^[^rnbqkpRNBQKP]*[p]+[^rnbqkpRNBQKP]*[NB][^rnbqkpRNBQKP]*$'
		AND LENGTH(REPLACE(FEN, ' ', '')) = 10 THEN 'Pawns v Minor'
END;


UPDATE book
SET Focus_Area = CASE
	WHEN Description LIKE '%opening%' AND Description NOT LIKE '%endgame%' AND Description NOT LIKE '%tactic%' THEN 'Openings'
	WHEN Description LIKE '%endgame%' AND Description NOT LIKE '%opening%' AND Description NOT LIKE '%tactic%' THEN 'Endgames'
	WHEN Description LIKE '%tactic%' AND Description NOT LIKE '%opening%' AND Description NOT LIKE '%endgame%'THEN 'Tactics'
	ELSE 'General'
END;


UPDATE book
SET Openings = (
	SELECT GROUP_CONCAT(o.Name SEPARATOR ',  ')
	FROM opening o
	WHERE book.Description LIKE CONCAT('%', o.Name, '%')
);


INSERT INTO book_opening (Book_Title, Opening_FEN)
SELECT 
    b.Title AS Book_Title,
    o.FEN AS Opening_FEN
FROM 
    book b
JOIN 
    opening o
ON 
    b.Description LIKE CONCAT('%', o.Name, '%');

