Twitterのbotのソースコードの管理を練習がてらBitbucketでやってます。

---

* ごちゃごちゃ書いてますが、以下のことをしています。

  1. 鍵アカでないフォロワーのツイートの内容（ログ）を読み込み
  1. MeCabに投げて形態素分解
  1. 2個の形態素までを考慮したマルコフ連鎖でつぶやきを生成
  1. つぶやく    


* 一日4回ぐらいつぶやいてます。
  
  * 編集している時などに大量のつぶやきをしてTLを汚すことがあるかもしれません。ごめんなさい。   


* 結局誰のつぶやきが使われるの？
  
  * 本botがフォローしている人ではなく
  * 本botをフォローしている人のログを読み込みます。    

