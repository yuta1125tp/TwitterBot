Twitterのbotのソースコードの管理を練習がてらBitbucketでやってます。

---

ごちゃごちゃ書いてますが、以下のことをしています。

   1. 鍵アカでないフォロワーのツイートの内容（ログ）を読み込み
   2. MeCabに投げて形態素分解
   3. 2個の形態素までを考慮したマルコフ連鎖でつぶやきを生成
   4. つぶやく    

一日4回ぐらいつぶやいてます。
  
   編集している時などに大量のつぶやきをしてTLを汚すことがあるかもしれません。ごめんなさい。   


結局誰のつぶやきが使われるの？
  
  * 本bot**が**フォローしている人ではなく
  * 本bot**を**フォローしている人のログを読み込みます。    

