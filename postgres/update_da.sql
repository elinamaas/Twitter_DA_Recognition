update annotated_token_tweet
set dialogue_act_id = (select dialogue_act.dialogue_act_id as da_id
			from dialogue_act
			where dialogue_act.dialogue_act_name = 'IT_IP')
where tweet_id = 403155252800929792 and token_offset =26;


select * from annotated_token_tweet where tweet_id = 403155252800929792;

select * from segmentation where tweet_id = 403155252800929792;


DELETE FROM segmentation
WHERE tweet_id = 403155252800929792 and segmentation_offsets = '26:26';

update segmentation
set segmentation_offsets = '4:26'
where tweet_id = 404584973396877312 and segmentation_offsets = '4:25';

select * from segmentation where tweet_id = 404584973396877312;

update segmentation
set dialogue_act_id = (select dialogue_act.dialogue_act_id as da_id
			from dialogue_act
			where dialogue_act.dialogue_act_name = 'IT_IP_Inform_Agreement')
where tweet_id = 405323801920958464 and segmentation_offsets = '5:9'

INSERT INTO segmentation (tweet_id,segmentation_offsets,dialogue_act_id)
VALUES (403047339058667520,'8:9',(select dialogue_act.dialogue_act_id as da_id
			from dialogue_act
			where dialogue_act.dialogue_act_name = 'IT_IP'));