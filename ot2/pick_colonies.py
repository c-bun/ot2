from typing import Tuple, List
from opentrons import protocol_api
from opentrons.types import Location
import time
import json
import csv

# metadata
metadata = {
    "protocolName": "Coloy Picker",
    "author": "Colin Rathbun <rathbunc@dickinson.edu>",
    "description": "Given a CSV of colony locations, pick the colonies and innoculate them in 96 well plates.",
    "apiLevel": "2.12",
}

# This should be False when not testing
TESTING = True

# Other hardcoded parameters
NUMBER_OF_96_WELL_PLATES = 2  # This can only be between 1 and 4.

# Paste CSV files here. This can only be between 1 and 3 dishes. There MUST be enogh colonies in the csv to fill all plates.
PLATE_CSVs = {
    1: """
    ,x coord,y coord,quality,x mm,y mm,x%,y%
0,488,193,1.0,14.57138263665595,9.54726688102894,0.2456610071087575,0.2324915836120526
1,418,470,0.9375,4.566559485530546,-30.04324758842444,0.07698827422288707,-0.7316022790314
2,81,216,0.9375,-43.59951768488746,6.2599678456591645,-0.735050454099089,0.15244046866331828
3,380,274,0.90625,-0.8646302250803859,-2.029742765273312,-0.014576923629442568,-0.04942756033783787
4,415,404,0.875,4.137781350482315,-20.610128617363348,0.06975944281349263,-0.501890383961119
5,103,188,0.875,-40.455144694533764,10.261897106109325,-0.6820390237635298,0.2498939999052557
6,291,179,0.84375,-13.585048231511255,11.54823151125402,-0.2290322554414778,0.2812183492330213
7,457,21,0.84375,10.140675241157556,34.13054662379421,0.17096308254501486,0.8311347040982396
8,386,173,0.8125,-0.0070739549839228255,12.405787781350483,-0.00011926081065367657,0.30210124878486505
9,390,23,0.8125,0.5646302250803859,33.84469453376206,0.009519181068538917,0.8241737375809585
10,73,306,0.8125,-44.74292604501608,-6.603376205787781,-0.7543273378574742,-0.1608030246143378
11,541,36,0.78125,22.14646302250804,31.986655948553054,0.37337036200805934,0.7789274552186304
12,7,69,0.96875,-54.17604501607717,27.270096463022508,-0.913361628864152,0.6640715076834898
13,308,349,0.75,-11.155305466237943,-12.7491961414791,-0.18806887745490927,-0.3104638047358846
14,748,256,0.75,51.73215434083602,0.5429260450160772,0.8721597292562762,0.013221138317693346
15,469,95,0.75,11.855787781350482,23.5540192926045,0.19987840818259264,0.5735789429588336
16,337,171,0.9375,-7.010450160771705,12.691639871382637,-0.11819017383076297,0.30906221530214634
17,423,132,0.90625,5.281189710610932,18.265755627009646,0.08903632657187781,0.4448010623891306
18,680,134,0.90625,42.01318327974277,17.979903536977492,0.708306217310002,0.43784009587184936
19,46,29,0.71875,-48.60192926045016,32.98713826366559,-0.8193868205420242,0.8032908380291147
20,672,323,0.71875,40.86977491961415,-9.033118971061093,0.6890293335516169,-0.2199712400112284
21,41,141,0.71875,-49.31655948553055,16.97942122186495,-0.8314348728910149,0.4134767130613649
22,324,88,0.71875,-8.868488745980708,24.55450160771704,-0.14951510993813888,0.5979423257693179
23,76,243,0.875,-44.31414790996784,2.40096463022508,-0.7470985064480796,0.05846742068002144
24,505,200,0.875,17.00112540192926,8.546784565916399,0.286624385095326,0.20812820080156821
25,225,63,0.6875,-23.018167202572346,28.12765273311897,-0.3880665464481556,0.6849544072353335
26,207,505,0.6875,-25.590836012861736,-35.04565916398714,-0.43143953490452225,-0.8534191930838217
27,23,46,0.6875,-51.88922829581993,30.55739549839228,-0.8748078613473815,0.7441226226322242
28,546,160,0.84375,22.861093247588425,14.263826366559487,0.3854184143570501,0.3473475311471932
29,350,201,0.84375,-5.152411575562701,8.403858520900322,-0.08686523772338703,0.2046477175429276
30,445,25,0.65625,8.42556270096463,33.5588424437299,0.14204775690743707,0.8172127710636772
31,473,283,0.65625,12.427491961414791,-3.3160771704180068,0.20951685006178525,-0.08075190966560349
32,580,276,0.9750000000000005,27.72057877813505,-2.3155948553054664,0.46734517033018713,-0.056388526855119116
33,542,127,0.8125,22.289389067524116,18.98038585209003,0.3757799724778575,0.46220347868233363
34,318,71,0.8125,-9.72604501607717,26.984244372990354,-0.1639727727569278,0.6571105411662086
35,312,479,0.8125,-10.583601286173634,-31.329581993569136,-0.17843043557571667,-0.7629266283591657
36,225,312,0.8125,-23.018167202572346,-7.460932475884245,-0.3880665464481556,-0.18168592416618154
37,672,184,0.78125,40.86977491961415,10.833601286173634,0.6890293335516169,0.2638159329398182
38,72,412,0.625,-44.88585209003215,-21.75353697749196,-0.7567369483272722,-0.5297342500302439
39,47,20,0.625,-48.45900321543408,34.273472668810285,-0.8169772100722259,0.8346151873568802
40,528,116,0.75,20.28842443729904,20.55257234726688,0.3420454259006835,0.5004887945273806
41,554,43,0.75,24.004501607717042,30.986173633440515,0.40469529811543525,0.754564072408146
42,386,43,0.59375,-0.0070739549839228255,30.986173633440515,-0.00011926081065367657,0.754564072408146
43,228,50,0.59375,-22.589389067524113,29.985691318327973,-0.38083771503876107,0.7302006895976616
44,315,119,0.59375,-10.154823151125402,20.123794212218648,-0.1712016041663222,0.49004734475145867
45,379,262,0.71875,-1.007556270096463,-0.31463022508038585,-0.016986534099240717,-0.007661761234150392
46,663,194,0.71875,39.58344051446946,9.404340836012862,0.6673428393234335,0.22901110035341196
47,560,392,0.5625,24.862057877813506,-18.89501607717042,0.41915296093422416,-0.46012458485743146
48,277,25,0.8250000000000004,-15.586012861736336,33.5588424437299,-0.2627668020186519,0.8172127710636772
49,467,217,0.6875,11.569935691318328,6.117041800643087,0.19505918724299634,0.14895998540467764
50,283,353,0.6875,-14.728456591639873,-13.320900321543409,-0.248309139199863,-0.3243857377704471
51,692,258,0.6875,43.728295819935695,0.2570739549839228,0.7372215429475798,0.006260171800412099
52,579,308,0.8000000000000004,27.577652733118974,-6.889228295819936,0.46493555986038904,-0.16776399113161905
53,508,30,0.8000000000000004,17.429903536977495,32.84421221864952,0.29385321650472046,0.7998103547704741
54,90,150,0.53125,-42.313183279742766,15.693086816720259,-0.7133639598709056,0.3821523637335994
55,206,311,0.53125,-25.73376205787781,-7.318006430868167,-0.43384914537432034,-0.17820544090754092
56,317,338,0.53125,-9.868971061093248,-11.17700964630225,-0.16638238322672594,-0.27217848889083773
57,21,451,0.53125,-52.17508038585209,-27.327652733118974,-0.8796270822869778,-0.6654730971172282
58,732,215,0.65625,49.44533762057878,6.402893890675242,0.8336059617395057,0.1559209519219589
59,282,323,0.65625,-14.87138263665595,-9.033118971061093,-0.2507187496696611,-0.2199712400112284
60,709,307,0.7750000000000004,46.158038585209006,-6.746302250803859,0.7781849209341484,-0.16428350787297843
61,419,201,0.7500000000000003,4.709485530546623,8.403858520900322,0.07939788469268522,0.2046477175429276
62,653,231,0.7500000000000003,38.15418006430868,4.116077170418007,0.643246734625452,0.10023321978370892
63,298,37,0.625,-12.584565916398715,31.84372990353698,-0.21216498215289076,0.7754469719599898
64,221,81,0.625,-23.589871382636655,25.55498392282958,-0.3977049883273482,0.6223057085798024
65,265,175,0.625,-17.30112540192926,12.119935691318329,-0.2916821276562296,0.2951402822675838
66,530,201,0.7250000000000003,20.574276527331193,8.403858520900322,0.34686464684027973,0.2046477175429276
67,152,212,0.7250000000000003,-33.45176848874598,6.831672025723473,-0.5639681107434203,0.16636240169788077
68,504,297,0.7000000000000003,16.858199356913186,-5.317041800643087,0.2842147746255279,-0.1294786752865722
69,616,305,0.7000000000000003,32.86591639871383,-6.460450160771704,0.5540911472429205,-0.15732254135569718
70,526,360,0.5625,20.002572347266884,-14.32138263665595,0.3372262049610872,-0.34874912058093144
71,125,2,0.53125,-37.31077170418006,36.84614147909968,-0.6290275934279704,0.8972638860124116
72,536,146,0.53125,21.431832797427653,16.264790996784566,0.3613223096590686,0.39607429676816186
73,620,173,0.7291666666666669,33.43762057877814,12.405787781350483,0.5637295891221131,0.30210124878486505
74,648,251,0.625,37.4395498392283,1.257556270096463,0.6311986822764613,0.03062355461089646
""",
    2: """
,x coord,y coord,quality,x mm,y mm,x%,y%
0,762,58,0.9375,53.733118971061096,28.842282958199355,0.9058942758334502,0.7023568235285367
1,133,491,0.875,-36.167363344051445,-33.04469453376206,-0.6097507096695852,-0.8046924274628531
2,369,212,0.875,-2.4368167202572346,6.831672025723473,-0.041082638797222196,0.16636240169788077
3,336,505,0.84375,-7.153376205787782,-35.04565916398714,-0.12059978430056112,-0.8534191930838217
4,435,472,0.84375,6.996302250803859,-30.329099678456593,0.1179516522094556,-0.7385632455486812
5,504,442,0.8125,16.858199356913186,-26.041318327974277,0.2842147746255279,-0.6341487477894625
6,365,373,0.8125,-3.0085209003215434,-16.179421221864953,-0.050721080676414794,-0.3939954029432596
7,488,478,1.0,14.57138263665595,-31.186655948553057,0.2456610071087575,-0.759446145100525
8,280,70,1.0,-15.157234726688104,27.12717041800643,-0.2555379706092574,0.6605910244248492
9,425,125,1.0,5.567041800643087,19.266237942122185,0.09385554751147411,0.4691644451996149
10,475,376,1.0,12.713344051446946,-16.608199356913186,0.21433607100138155,-0.40443685271918145
11,498,345,0.96875,16.000643086816723,-12.177491961414791,0.269757111806739,-0.29654187170132207
12,72,95,0.90625,-44.88585209003215,23.5540192926045,-0.7567369483272722,0.5735789429588336
13,361,20,0.90625,-3.580225080385852,34.273472668810285,-0.06035952255560739,0.8346151873568802
14,225,113,0.90625,-23.018167202572346,20.98135048231511,-0.3880665464481556,0.5109302443033024
15,204,484,0.90625,-26.019614147909966,-32.04421221864952,-0.43866836631391665,-0.7803290446523687
16,216,128,0.71875,-24.30450160771704,18.837459807073955,-0.4097530406763389,0.4587229954236931
17,628,31,0.875,34.581028938906755,32.70128617363344,0.5830064728804983,0.7963298715118335
18,514,51,0.875,18.287459807073958,29.842765273311898,0.30831087932350937,0.726720206339021
19,697,85,0.875,44.44292604501608,24.983279742765273,0.7492695952965706,0.6083837755452398
20,103,338,0.875,-40.455144694533764,-11.17700964630225,-0.6820390237635298,-0.27217848889083773
21,75,466,0.875,-44.45707395498392,-29.47154340836013,-0.7495081169178778,-0.7176803459968375
22,468,407,0.6875,11.712861736334405,-21.038906752411577,0.1974687977127945,-0.5123318337370407
23,606,29,0.84375,31.436655948553057,32.98713826366559,0.529995042544939,0.8032908380291147
24,292,217,0.84375,-13.442122186495178,6.117041800643087,-0.22662264497167964,0.14895998540467764
25,239,449,0.65625,-21.017202572347266,-27.04180064308682,-0.35433199987098146,-0.658512130599947
26,351,364,0.65625,-5.009485530546624,-14.893086816720258,-0.08445562725358888,-0.36267105361549395
27,475,287,0.8125,12.713344051446946,-3.887781350482315,0.21433607100138155,-0.09467384270016596
28,679,462,0.8125,41.870257234726694,-28.89983922829582,0.7058966068402039,-0.703758412962275
29,658,420,0.8125,38.86881028938907,-22.89694533762058,0.6552947869744427,-0.5575781160993688
30,459,348,0.8125,10.42652733118971,-12.606270096463023,0.17578230348461116,-0.30698332147724394
31,144,280,0.8125,-34.595176848874594,-2.887299035369775,-0.5832449945018056,-0.07031045988968161
32,579,169,0.8125,27.577652733118974,12.977491961414792,0.46493555986038904,0.31602318181942757
33,414,504,0.78125,3.994855305466238,-34.902733118971064,0.06734983234369447,-0.8499387098251812
34,494,459,0.625,15.428938906752412,-28.47106109324759,0.26011866992754634,-0.6933169631863532
35,538,334,0.78125,21.717684887459807,-10.605305466237942,0.3661415305986649,-0.2582565558562752
36,519,480,0.78125,19.002090032154342,-31.47250803858521,0.32035893167250007,-0.7664071116178063
37,98,470,0.78125,-41.16977491961415,-30.04324758842444,-0.6940870761125204,-0.7316022790314
38,133,425,0.78125,-36.167363344051445,-23.611575562700967,-0.6097507096695852,-0.574980532392572
39,169,420,0.78125,-31.02202572347267,-22.89694533762058,-0.5230047327568519,-0.5575781160993688
40,427,408,0.78125,5.852893890675241,-21.181832797427653,0.09867476845107041,-0.5158123169956813
41,201,131,0.9250000000000005,-26.4483922829582,18.408681672025722,-0.44589719772331116,0.4482815456477712
42,251,115,0.9250000000000005,-19.30209003215434,20.695498392282957,-0.3254166742334037,0.5039692777860212
43,330,233,0.9000000000000005,-8.010932475884244,3.830225080385852,-0.13505744711935,0.09327225326642767
44,253,442,0.75,-19.016237942122185,-26.041318327974277,-0.3205974532938074,-0.6341487477894625
45,114,404,0.75,-38.882958199356914,-20.610128617363348,-0.6555333085957501,-0.501890383961119
46,334,322,0.75,-7.4392282958199365,-8.890192926045016,-0.12541900524015742,-0.21649075675258775
47,492,164,0.75,15.143086816720258,13.692122186495178,0.2552994489879501,0.3334255981126307
48,40,447,0.75,-49.45948553054662,-26.755948553054665,-0.8338444833608131,-0.6515511640826657
49,734,66,0.75,49.731189710610934,27.698874598070738,0.838425182679102,0.6745129574594116
50,510,376,0.59375,17.71575562700965,-16.608199356913186,0.29867243744431676,-0.40443685271918145
51,737,196,0.59375,50.15996784565917,9.118488745980708,0.8456540140884965,0.22205013383613073
52,362,388,0.59375,-3.437299035369775,-18.323311897106112,-0.05794991208580924,-0.44620265182286895
53,326,310,0.59375,-8.582636655948553,-7.17508038585209,-0.14469588899854258,-0.17472495764890028
54,471,275,0.59375,12.141639871382637,-2.172668810289389,0.20469762912218895,-0.05290804359647849
55,4,502,0.59375,-54.6048231511254,-34.616881028938906,-0.9205904602735464,-0.8429777433078999
56,435,383,0.8750000000000004,6.996302250803859,-17.608681672025725,0.1179516522094556,-0.4288002355296658
57,394,283,0.71875,1.1363344051446946,-3.3160771704180068,0.019157622947731514,-0.08075190966560349
58,558,92,0.71875,24.57620578778135,23.98279742765273,0.41433373999462786,0.5840203927347555
59,739,502,0.71875,50.44581993569132,-34.616881028938906,0.8504732350280927,-0.8429777433078999
60,292,313,0.71875,-13.442122186495178,-7.603858520900321,-0.22662264497167964,-0.18516640742482215
61,235,195,0.71875,-21.588906752411575,9.261414790996785,-0.36397044175017407,0.22553061709477135
62,652,164,0.8500000000000004,38.01125401929261,13.692122186495178,0.6408371241556539,0.3334255981126307
63,719,311,0.8500000000000004,47.587299035369774,-7.318006430868167,0.8022810256321298,-0.17820544090754092
64,83,481,0.8500000000000004,-43.3136655948553,-31.615434083601286,-0.7302312331594926,-0.7698875948764468
65,728,178,0.5625,48.873633440514475,11.691157556270097,0.8239675198603131,0.28469883249166195
66,447,439,0.5625,8.711414790996784,-25.612540192926048,0.14686697784703337,-0.6237072980135407
67,426,501,0.5625,5.709967845659164,-34.47395498392283,0.09626515798127226,-0.8394972600492593
68,530,442,0.8250000000000004,20.574276527331193,-26.041318327974277,0.34686464684027973,-0.6341487477894625
69,701,401,0.8250000000000004,45.01463022508039,-20.181350482315114,0.7589080371757632,-0.49144893418519703
70,749,21,0.8250000000000004,51.875080385852094,34.13054662379421,0.8745693397260743,0.8311347040982396
71,322,424,0.6875,-9.154340836012862,-23.468649517684888,-0.15433433087773518,-0.5715000491339313
72,131,385,0.6875,-36.4532154340836,-17.89453376205788,-0.6145699306091815,-0.435761202046947
73,494,384,0.6875,15.428938906752412,-17.751607717041804,0.26011866992754634,-0.43228071878830643
74,127,367,0.6875,-37.02491961414791,-15.32186495176849,-0.6242083724883741,-0.37311250339141583
75,298,331,0.6875,-12.584565916398715,-10.17652733118971,-0.21216498215289076,-0.24781510608035337
76,84,203,0.6875,-43.170739549839226,8.118006430868167,-0.7278216226896945,0.19768675102564637
77,431,153,0.6875,6.42459807073955,15.264308681672027,0.108313210330263,0.3717109139576775
78,397,467,0.8000000000000004,1.5651125401929262,-29.61446945337621,0.02638645435712596,-0.7211608292554782
79,555,347,0.8000000000000004,24.14742765273312,-12.463344051446946,0.40710490858523346,-0.30350283821860335
80,326,354,0.53125,-8.582636655948553,-13.463826366559486,-0.14469588899854258,-0.3278662210290877
81,671,344,0.53125,40.726848874598076,-12.034565916398714,0.6866197230818187,-0.2930613884426815
82,540,488,0.53125,22.00353697749196,-32.61591639871383,0.3709607515382612,-0.7942509776869312
83,220,484,0.53125,-23.73279742765273,-32.04421221864952,-0.4001145987971463,-0.7803290446523687
84,554,483,0.53125,24.004501607717042,-31.901286173633444,0.40469529811543525,-0.7768485613937282
85,530,502,0.53125,20.574276527331193,-34.616881028938906,0.34686464684027973,-0.8429777433078999
86,90,151,0.53125,-42.313183279742766,15.550160771704181,-0.7133639598709056,0.37867188047495876
87,347,126,0.65625,-5.581189710610933,19.12331189710611,-0.09409406913278147,0.46568396194097433
88,479,179,0.65625,13.285048231511254,11.54823151125402,0.22397451288057413,0.2812183492330213
89,217,304,0.65625,-24.161575562700964,-6.317524115755627,-0.40734343020654074,-0.15384205809705656
90,42,376,0.65625,-49.17363344051447,-16.608199356913186,-0.8290252624212168,-0.40443685271918145
91,675,272,0.9166666666666672,41.298553054662385,-1.7438906752411576,0.6962581649610113,-0.04246659382055662
92,241,253,0.7750000000000004,-20.73135048231511,0.9717041800643087,-0.34951277893138516,0.023662588093615215
93,634,217,0.8750000000000004,35.438585209003215,6.117041800643087,0.5974641356992871,0.14895998540467764
94,206,173,0.7500000000000003,-25.73376205787781,12.405787781350483,-0.43384914537432034,0.30210124878486505
95,346,412,0.7500000000000003,-5.72411575562701,-21.75353697749196,-0.09650367960257962,-0.5297342500302439
96,180,466,0.7500000000000003,-29.44983922829582,-29.47154340836013,-0.4964990175890722,-0.7176803459968375
97,700,498,0.7500000000000003,44.87170418006431,-34.0451768488746,0.756498426705965,-0.8290558102733374
98,518,320,0.625,18.859163987138267,-8.604340836012861,0.317949321202702,-0.20952979023530652
99,4,352,0.625,-54.6048231511254,-13.177974276527332,-0.9205904602735464,-0.32090525451180646
102,298,508,0.625,-12.584565916398715,-35.47443729903537,-0.21216498215289076,-0.8638606428597437
106,218,455,0.625,-24.018649517684885,-27.899356913183283,-0.4049338197367426,-0.6793950301517907
109,742,290,0.7250000000000003,50.87459807073955,-4.316559485530546,0.8577020664374873,-0.10511529247608782
110,425,315,0.7250000000000003,5.567041800643087,-7.889710610932475,0.09385554751147411,-0.19212737394210339
111,684,218,0.8333333333333337,42.58488745980708,5.97411575562701,0.7179446591891946,0.14547950214603703
112,710,96,0.59375,46.30096463022508,23.411093247588422,0.7805945314039464,0.5700984597001929
113,487,240,0.59375,14.428456591639872,2.829742765273312,0.24325139663895934,0.06890887045594331
114,479,511,0.59375,13.285048231511254,-35.903215434083606,0.22397451288057413,-0.8743020926356656
115,529,323,0.7000000000000003,20.431350482315114,-9.033118971061093,0.3444550363704816,-0.2199712400112284
116,649,112,0.7000000000000003,37.582475884244374,21.12427652733119,0.6336082927462594,0.5144107275619431
117,261,506,0.6750000000000003,-17.872829581993567,-35.188585209003215,-0.3013205695354222,-0.8568996763424623
118,656,365,0.6750000000000003,38.582958199356916,-15.036012861736335,0.6504755660348465,-0.36615153687413454
""",
}

# not sure where to put this
colonies_picked = 0


def populate_deck(
    protocol: protocol_api.ProtocolContext,
    next_open_position=11,
):

    # Load in the tipracks.
    tip_racks = [
        protocol.load_labware("opentrons_96_tiprack_20ul", next_open_position - i)
        for i in range(NUMBER_OF_96_WELL_PLATES)
    ]
    next_open_position -= len(tip_racks)

    if TESTING:
        deepwell_plates = [
            protocol.load_labware_from_definition(
                json.load(
                    open(
                        "../labware/labcon_96_wellplate_2200ul/labcon_96_wellplate_2200ul.json"
                    )
                ),
                next_open_position - i,
            )
            for i in range(NUMBER_OF_96_WELL_PLATES)
        ]
        next_open_position -= len(deepwell_plates)

        petri_dishes = [
            protocol.load_labware_from_definition(
                json.load(
                    open(
                        "../labware/celltreat_1_wellplate_48000ul/celltreat_1_wellplate_48000ul.json"
                    )
                ),
                next_open_position - i,
            )
            for i in range(len(PLATE_CSVs))
        ]
        next_open_position -= len(petri_dishes)
    else:
        deepwell_plates = [
            protocol.load_labware("labcon_96_wellplate_2200ul", next_open_position - i)
            for i in range(NUMBER_OF_96_WELL_PLATES)
        ]
        next_open_position -= len(deepwell_plates)

        petri_dishes = [
            protocol.load_labware(
                "celltreat_1_wellplate_48000ul", next_open_position - i
            )
            for i in range(len(PLATE_CSVs))
        ]
        next_open_position -= len(petri_dishes)

    return tip_racks, deepwell_plates, petri_dishes


def pick_colony(
    pipette: protocol_api.InstrumentContext,
    petri_dish: protocol_api.labware.Labware,
    colony_location: tuple,
):
    """
    Given a plate location and a colony location, pick a colony.
    """
    # Get the colony location in the plate coordinate system.
    x, y = colony_location

    # TODO I'm guessing on all these parameters. Verify first in the lab.
    pipette.pick_up_tip()

    # Move to the colony location. Dip down into the petri dish. Pull back up.
    pipette.move_to(
        Location(petri_dish.wells()[0].from_center_cartesian(x=x, y=y, z=1), petri_dish)
    )  # TODO make sure z is correct. How do we set this as an offest?
    pipette.move_to(
        Location(
            petri_dish.wells()[0].from_center_cartesian(x=x, y=y, z=-1), petri_dish
        )
    )
    pipette.move_to(
        Location(petri_dish.wells()[0].from_center_cartesian(x=x, y=y, z=1), petri_dish)
    )


def innoculate_colony(
    pipette: protocol_api.InstrumentContext,
    deepwell_plates: List[protocol_api.labware.Labware],
):
    """
    With a picked colony on the tip of the pipette, innoculate the colony in the next availble well.
    """
    global colonies_picked
    plate = deepwell_plates[colonies_picked // 96]
    well = plate.wells()[colonies_picked % 96]
    pipette.aspirate(10, well)
    pipette.dispense(10, well)
    pipette.aspirate(10, well)
    pipette.dispense(10, well)
    pipette.drop_tip()
    colonies_picked += 1


def run(protocol: protocol_api.ProtocolContext):

    tip_racks, deepwell_plates, petri_dishes = populate_deck(protocol)

    # pipettes
    left_pipette = protocol.load_instrument(
        "p20_single_gen2", "left", tip_racks=tip_racks
    )

    for plate, raw_csv in PLATE_CSVs.items():
        csv_data = raw_csv.splitlines()[1:]  # Discard the blank first line.
        colonies = csv.DictReader(csv_data)
        for i, colony in enumerate(colonies):
            if colonies_picked < (96 * len(deepwell_plates)):
                print(
                    "Picking colony {} of {} from {} at x={} and y={}".format(
                        i + 1,
                        len(deepwell_plates * 96),
                        plate,
                        colony["x%"],
                        colony["y%"],
                    )
                )
                pick_colony(
                    left_pipette,
                    petri_dishes[plate - 1],
                    # (
                    #     "%.3f" % float(colony["x%"]),
                    #     "%.3f" % float(colony["y%"]),
                    # ),  # because there are too many decimal places in the csv?
                    (float(colony["x%"]), float(colony["y%"])),
                )
                if i < 4:
                    # pause to make sure that the tip is in the right spot
                    protocol.pause("Is the tip in the right spot?")
                innoculate_colony(left_pipette, deepwell_plates)
            else:
                print("Done with all plates.")
                break
