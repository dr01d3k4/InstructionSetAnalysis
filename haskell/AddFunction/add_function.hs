module Main where


add :: Int -> Int -> Int
add x y = x + y


main :: IO ()
main = do
	putStrLn "Hello world!"
	let x = 5
	let y = 7
	let z = add x y
	print z

