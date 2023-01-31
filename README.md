# Tweet Sentiment Score API

## Sentiment Score Formula

Sentiment Score is depicted as scale from -2 to +2. The scale can be interpreted as follows:
* Sentiment Score towards -2 meaning that people react to the keyword **NEGATIVELY**.
* Sentiment Score towards +2 meaning that people react to the keyword **POSITIVELY**.
* Sentiment Score on 0 meaning that people react to the keyword **NEUTRALLY**.

#### Algorithm
1. Any occurence of Positive word and Negative word will be initialized as a ***scalar***.<br>
2. Any occurence of Booster words will be calculated as the ***magnitude***.<br>
3. Any occurence of Negation words will be ***counter the polarity*** at the end of the calculation.<br>
4. At the end average of the score from 200 tweets are normalized to the specified scale.
