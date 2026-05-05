"""
Corpus de test pour le module de prétraitement
45 tweets réalistes en 5 langues (fr, en, es, de, ar)
9 thèmes : ia, environnement, sport, politique, sante, economie, education, culture, technologie
5 tweets par thème × 9 thèmes = 45 tweets
"""

CORPUS = [

    # ═══════════════════════════════════════════
    #  THÈME 1 : INTELLIGENCE ARTIFICIELLE
    # ═══════════════════════════════════════════
    {
        'id': 1,
        'language': 'fr',
        'category': 'ia',
        'text': "ChatGPT vient de rédiger un rapport complet à ma place en 30 secondes. Je suis bluffé mais aussi un peu inquiet pour l'avenir de mon métier. L'intelligence artificielle générative est en train de tout bouleverser : rédaction, code, design, analyse de données. Les entreprises qui n'adoptent pas ces outils maintenant vont se retrouver à la traîne dans 2 ans. La question n'est plus 'est-ce que l'IA va changer le monde ?' mais 'à quelle vitesse ?' #IA #ChatGPT #FutureOfWork #Technologie"
    },
    {
        'id': 2,
        'language': 'en',
        'category': 'ia',
        'text': "Just tested GPT-4 on a medical diagnosis task and the results were honestly terrifying in the best way possible. It identified a rare condition from symptom descriptions that junior doctors missed. We're entering an era where AI will be the first line of diagnosis in healthcare. This isn't science fiction anymore. The ethical implications are enormous — who's responsible when the AI is wrong? We need regulation NOW before this gets out of hand. #AI #HealthcareAI #MachineLearning #Ethics"
    },
    {
        'id': 3,
        'language': 'es',
        'category': 'ia',
        'text': "La inteligencia artificial está transformando el mercado laboral de una manera que nunca habíamos visto antes. Según un nuevo informe, el 40% de los empleos actuales podrían ser automatizados en la próxima década. No se trata solo de trabajos manuales — los abogados, contadores y periodistas también están en riesgo. Sin embargo, la IA también está creando nuevas profesiones que ni siquiera existían hace cinco años. La clave es adaptarse y aprender continuamente. #InteligenciaArtificial #FuturoDelTrabajo #Automatización"
    },
    {
        'id': 4,
        'language': 'de',
        'category': 'ia',
        'text': "Künstliche Intelligenz revolutioniert die deutsche Industrie in einem atemberaubenden Tempo. BMW und Siemens setzen bereits KI-gestützte Systeme in der Produktion ein, die Fehler erkennen bevor sie entstehen. Das spart Millionen und macht unsere Produkte konkurrenzfähiger. Aber wir müssen auch an die Arbeitnehmer denken — Umschulung und lebenslanges Lernen werden zur Pflicht. Deutschland muss jetzt investieren, um im globalen KI-Rennen nicht zurückzufallen. #KünstlicheIntelligenz #Industrie40 #Innovation"
    },
    {
        'id': 5,
        'language': 'ar',
        'category': 'ia',
        'text': "الذكاء الاصطناعي يغير قواعد اللعبة في عالم التعليم العربي. منصات مثل خان أكاديمي وكورسيرا تستخدم الآن خوارزميات ذكية تتكيف مع مستوى كل طالب وتقدم له محتوى مخصصاً. تخيل أن يكون لكل طالب معلم خاص متاح على مدار الساعة. هذا ليس مستقبلاً بعيداً بل هو واقع يتشكل الآن. على الحكومات العربية الاستثمار في هذه التقنيات لتحسين جودة التعليم وتقليص الفجوة التعليمية. #الذكاء_الاصطناعي #التعليم #تكنولوجيا"
    },

    # ═══════════════════════════════════════════
    #  THÈME 2 : ENVIRONNEMENT / CLIMAT
    # ═══════════════════════════════════════════
    {
        'id': 6,
        'language': 'fr',
        'category': 'environnement',
        'text': "Les images des incendies en Amazonie cette année sont insupportables. Des millions d'hectares partis en fumée, des espèces disparues à jamais, des communautés autochtones déplacées. Et nos dirigeants continuent de se retrouver en sommet climatique pour signer des accords qu'ils ne respectent pas. La COP doit devenir contraignante avec de vraies sanctions pour les pays qui ne tiennent pas leurs engagements. On n'a plus le temps pour la diplomatie de façade. #Amazonie #CrisClimatique #COP #Environnement"
    },
    {
        'id': 7,
        'language': 'en',
        'category': 'environnement',
        'text': "Record-breaking heatwaves across Europe this summer killed thousands of people and yet some politicians still call climate change a hoax. The science is crystal clear — we are in a climate emergency and every year of inaction makes the future worse. Solar and wind energy are now cheaper than coal in most of the world. There is literally no economic argument left against the green transition. The only thing standing in the way is fossil fuel lobbying and political cowardice. #ClimateChange #GreenEnergy #ClimateEmergency"
    },
    {
        'id': 8,
        'language': 'es',
        'category': 'environnement',
        'text': "España está sufriendo las consecuencias del cambio climático de manera brutal este verano. Las temperaturas superaron los 45 grados en Andalucía, los ríos están secos y los agricultores están perdiendo sus cosechas. La sequía ya no es una excepción sino la nueva normalidad. Necesitamos una política hídrica urgente, inversión masiva en energías renovables y una transición ecológica justa que no deje atrás a los trabajadores de los sectores tradicionales. #CambioClimatico #Sequia #MedioAmbiente"
    },
    {
        'id': 9,
        'language': 'de',
        'category': 'environnement',
        'text': "Deutschland hat sein Klimaziel für 2030 wieder verfehlt. Die CO2-Emissionen sinken zu langsam, der Kohleausstieg kommt zu spät und die Wärmewende stockt. Dabei haben wir die Technologie und das Geld, um das Problem zu lösen. Was fehlt ist politischer Mut. Die nächste Generation wird uns fragen, warum wir nicht gehandelt haben als wir noch die Chance hatten. Wir schulden unseren Kindern eine lebenswerte Welt — nicht nur schöne Worte auf Klimagipfeln. #Klimaschutz #Energiewende #CO2"
    },
    {
        'id': 10,
        'language': 'ar',
        'category': 'environnement',
        'text': "موجات الحر القياسية التي ضربت المنطقة العربية هذا الصيف ليست مجرد أحوال جوية عادية بل هي نتيجة مباشرة لتغير المناخ الذي طالما حذر منه العلماء. درجات حرارة تجاوزت 50 درجة مئوية في الخليج العربي والعراق ومصر. المدن الساحلية العربية مهددة بارتفاع مستوى البحر. حان الوقت لأن تتبنى الدول العربية استراتيجيات جدية للطاقة الشمسية وترشيد استهلاك المياه. #تغير_المناخ #البيئة #الطاقة_الشمسية"
    },

    # ═══════════════════════════════════════════
    #  THÈME 3 : SPORT
    # ═══════════════════════════════════════════
    {
        'id': 11,
        'language': 'fr',
        'category': 'sport',
        'text': "Mbappé au Real Madrid c'est officiel et franchement je comprends le choix. Le projet sportif est inarrêtable, le stade Bernabeu rénové est une cathédrale du foot, et jouer aux côtés de Vinicius et Bellingham c'est une opportunité unique. Mais une partie de moi restera toujours triste pour le PSG qui a tout donné pour le garder. Le football reste un business avant tout et les meilleurs jouent là où ils peuvent gagner la Ligue des Champions. #Mbappé #RealMadrid #Football #LDC"
    },
    {
        'id': 12,
        'language': 'en',
        'category': 'sport',
        'text': "LeBron James at 39 years old is still putting up 25 points, 8 rebounds and 8 assists per game. This man is literally defying biology. The dedication, the diet, the recovery routine — he invests over a million dollars a year in his body and it shows. What he's doing has never been done before in NBA history. Whether you're a fan or not, you have to respect the discipline and professionalism he's shown over two decades at the highest level. #LeBron #NBA #Basketball #GOAT"
    },
    {
        'id': 13,
        'language': 'es',
        'category': 'sport',
        'text': "El Clásico de anoche fue simplemente espectacular. Real Madrid y Barcelona nos regalaron noventa minutos de fútbol total, con cinco goles, dos expulsiones y una remontada increíble en los últimos minutos. Este es el partido que define por qué el fútbol es el deporte más apasionante del mundo. Vinicius fue absolutamente imparable y Lewandowski respondió con un hat-trick. La Liga española sigue siendo la mejor liga del mundo sin ninguna duda. #ElClasico #RealMadrid #Barcelona #LaLiga"
    },
    {
        'id': 14,
        'language': 'de',
        'category': 'sport',
        'text': "Die deutsche Nationalmannschaft hat endlich wieder zu ihrer alten Stärke zurückgefunden. Das 4:1 gegen Frankreich war eine Demonstration von modernem schnellem Fußball mit Pressing und technischer Finesse. Nagelsmann hat die Mannschaft taktisch perfekt eingestellt. Mit dieser Leistung kann Deutschland bei der nächsten EM eine echte Rolle spielen. Die Jugend drängt nach vorne — Musiala und Wirtz sind die Zukunft des deutschen Fußballs. #DFB #Fussball #EM2024 #Deutschland"
    },
    {
        'id': 15,
        'language': 'ar',
        'category': 'sport',
        'text': "المنتخب المغربي يكتب التاريخ مرة أخرى ! الأسود وصلوا إلى نصف نهائي كأس أمم أفريقيا بعد أداء مبهر طوال البطولة. ما يقدمه هؤلاء اللاعبون من تضحية وشجاعة وانتماء يجعلك فخوراً بالانتماء لهذه الأمة. بونو في المرمى لا يُخترق والمهاجمون يحولون كل فرصة إلى هدف. المغرب يثبت أن كرة القدم الأفريقية العربية وصلت لمستوى عالمي حقيقي. #المغرب #كأس_أمم_أفريقيا #كرة_القدم"
    },

    # ═══════════════════════════════════════════
    #  THÈME 4 : POLITIQUE
    # ═══════════════════════════════════════════
    {
        'id': 16,
        'language': 'fr',
        'category': 'politique',
        'text': "Les résultats des élections européennes sont un signal d'alarme que les partis traditionnels ne peuvent plus ignorer. La montée des partis d'extrême droite dans presque tous les pays membres reflète une fracture profonde entre les élites politiques et les citoyens ordinaires. Les gens en ont assez de l'inflation, de l'immigration non maîtrisée et d'une Union Européenne perçue comme trop distante de leurs préoccupations quotidiennes. Il faut une refonte totale de la communication politique. #ElectionsEuropéennes #Politique #UE"
    },
    {
        'id': 17,
        'language': 'en',
        'category': 'politique',
        'text': "The US election campaign is already the most divisive in modern history and we're still months away from voting day. Both sides are talking past each other completely. One side lives in a world of facts and the other in a world of grievances and conspiracy theories. Social media algorithms amplify the most extreme voices because outrage drives engagement. We desperately need platform reform and media literacy education before democracy itself becomes the casualty. #USElection #Democracy #Politics"
    },
    {
        'id': 18,
        'language': 'es',
        'category': 'politique',
        'text': "La crisis política en España no tiene visos de resolverse pronto. La incapacidad de los partidos para llegar a acuerdos básicos está paralizando las reformas que el país necesita urgentemente — sanidad, vivienda, pensiones. Los ciudadanos estamos hartos de ver a los políticos pelearse mientras los problemas reales se acumulan. La polarización extrema nos tiene atrapados en un bucle de elecciones sin resultados. Necesitamos una cultura política nueva basada en el diálogo. #PoliticaEspañola #Democracia #España"
    },
    {
        'id': 19,
        'language': 'de',
        'category': 'politique',
        'text': "Die politische Lage in Deutschland ist so turbulent wie seit Jahrzehnten nicht mehr. Die Ampelkoalition streitet öffentlich über jeden Haushaltseuro während die AfD in Umfragen immer stärker wird. Das ist ein Alarmsignal für unsere Demokratie. Wenn die etablierten Parteien nicht liefern suchen die Menschen Alternativen — auch gefährliche. Wir brauchen eine ehrliche Diskussion über die echten Probleme: Wohnungsnot, Inflation und Fachkräftemangel. #DeutschePolitik #Bundestag #Demokratie"
    },
    {
        'id': 20,
        'language': 'ar',
        'category': 'politique',
        'text': "الأزمات السياسية المتتالية في المنطقة العربية تُثبت أن غياب الديمقراطية الحقيقية وسيادة القانون هو جذر كل المشكلات. حين لا تكون هناك مؤسسات مستقلة وقضاء نزيه وحرية صحافة تنهار الدول تحت ثقل الفساد والمحسوبية. الشعوب العربية تستحق قيادات تضع المصلحة العامة فوق مصالحها الضيقة. التغيير لن يأتي من الخارج بل من إرادة شعبية واعية وشبابية مثقفة ترفض الوضع الراهن. #الديمقراطية #السياسة #الحكم_الرشيد"
    },

    # ═══════════════════════════════════════════
    #  THÈME 5 : SANTÉ
    # ═══════════════════════════════════════════
    {
        'id': 21,
        'language': 'fr',
        'category': 'sante',
        'text': "La santé mentale est enfin en train de devenir un sujet de conversation normale en France et c'est une excellente nouvelle. Pendant trop longtemps consulter un psychologue était tabou. Aujourd'hui les jeunes en parlent ouvertement sur les réseaux sociaux et demandent de l'aide sans honte. Mais le système public ne suit pas — les délais d'attente sont de plusieurs mois et les consultations coûtent cher. Il faut urgemment rembourser intégralement les soins psychologiques. #SantéMentale #Psychologie #Santé"
    },
    {
        'id': 22,
        'language': 'en',
        'category': 'sante',
        'text': "The obesity epidemic is the public health crisis nobody wants to talk about honestly. Ultra-processed food is everywhere, it's cheap, it's addictive by design, and it's killing people slowly. We regulate tobacco aggressively — why not junk food? The new GLP-1 weight loss drugs like Ozempic are remarkable but they cost thousands per month and aren't accessible to most people. We need systemic change in food policy not just individual willpower shaming. #PublicHealth #Obesity #FoodPolicy #Healthcare"
    },
    {
        'id': 23,
        'language': 'es',
        'category': 'sante',
        'text': "La pandemia nos dejó lecciones que no debemos olvidar. El sistema sanitario español aguantó al límite gracias al sacrificio increíble de médicos, enfermeras y auxiliares que trabajaron sin descanso durante meses. Ahora el gobierno necesita invertir seriamente en reforzar la sanidad pública — más personal, mejores salarios, más camas hospitalarias. La salud no es un gasto, es una inversión en el capital humano del país. No podemos permitir que otra crisis nos pille con los mismos problemas. #SanidadPública #Salud #Pandemia"
    },
    {
        'id': 24,
        'language': 'de',
        'category': 'sante',
        'text': "Das deutsche Gesundheitssystem steht vor einem strukturellen Kollaps wenn wir nicht schnell handeln. Der Fachkräftemangel in der Pflege ist dramatisch — tausende Stellen sind unbesetzt, die vorhandenen Pflegekräfte arbeiten am Limit und viele denken ans Aufhören. Gleichzeitig wird die Bevölkerung älter und braucht mehr Pflege. Wir müssen die Pflegeberufe attraktiver machen durch bessere Bezahlung und kürzere Arbeitszeiten. #Gesundheit #Pflege #Gesundheitssystem #Deutschland"
    },
    {
        'id': 25,
        'language': 'ar',
        'category': 'sante',
        'text': "الصحة النفسية في العالم العربي لا تزال من المحظورات الاجتماعية التي يجب كسرها. ملايين العرب يعانون من الاكتئاب والقلق والضغوط النفسية في صمت لأن طلب المساعدة النفسية لا يزال مرتبطاً بالوصمة الاجتماعية. الأمراض النفسية أمراض كالأمراض الجسدية تماماً وتحتاج إلى علاج متخصص. نحتاج إلى حملات توعية واسعة وإدراج الصحة النفسية في منظومة الرعاية الصحية الأولية. #الصحة_النفسية #الصحة #الوعي"
    },

    # ═══════════════════════════════════════════
    #  THÈME 6 : ÉCONOMIE
    # ═══════════════════════════════════════════
    {
        'id': 26,
        'language': 'fr',
        'category': 'economie',
        'text': "La crise du logement en France est devenue une véritable catastrophe sociale. Les loyers ont augmenté de 30% en 5 ans dans les grandes villes, les primo-accédants ne peuvent plus acheter et les classes moyennes sont repoussées toujours plus loin des centres urbains. Les plateformes de location courte durée comme Airbnb ont littéralement asphyxié le marché immobilier. Il faut une politique du logement ambitieuse avec plus de construction de logements sociaux. #Logement #Immobilier #CriseDuLogement #France"
    },
    {
        'id': 27,
        'language': 'en',
        'category': 'economie',
        'text': "Inflation is finally cooling but the damage to working class families is already done. Groceries, rent, energy — everything costs 20-30% more than three years ago and wages haven't kept up for most people. The Fed raised interest rates aggressively which slowed inflation but also made mortgages unaffordable for millions of Americans. We solved the inflation problem by creating a housing crisis. The wealth gap between asset owners and everyone else has never been wider. #Inflation #Economy #HousingCrisis"
    },
    {
        'id': 28,
        'language': 'es',
        'category': 'economie',
        'text': "La economía española está creciendo más que la media europea pero ese crecimiento no está llegando a todos los ciudadanos por igual. El desempleo juvenil sigue siendo escandalosamente alto — más del 28% de los jóvenes no tienen trabajo. Los salarios reales han perdido poder adquisitivo frente a la inflación. Mientras tanto los grandes bancos reportan beneficios récord. Algo no funciona bien en la distribución de la riqueza y los poderes públicos deben actuar. #EconomiaEspañola #DesempleoJuvenil #Desigualdad"
    },
    {
        'id': 29,
        'language': 'de',
        'category': 'economie',
        'text': "Die deutsche Wirtschaft steckt in der Rezession und die Ursachen sind struktureller Natur. Hohe Energiekosten nach dem Ende des billigen russischen Gases, veraltete Industrien die den digitalen Wandel verschlafen haben und zu viel Bürokratie die Investitionen hemmt. Deutschland muss sich neu erfinden — mehr Investitionen in Digitalisierung, Bildung und erneuerbare Energien. Die Zeit des Aussitzens ist vorbei. #DeutscheWirtschaft #Rezession #Wirtschaft #Standort"
    },
    {
        'id': 30,
        'language': 'ar',
        'category': 'economie',
        'text': "التضخم الذي يضرب الاقتصادات العربية يُثقل كاهل المواطن العادي بشكل غير محتمل. أسعار المواد الغذائية والطاقة والإيجارات ارتفعت بشكل جنوني بينما الأجور ظلت ثابتة أو ارتفعت بمعدلات أقل بكثير. الطبقة الوسطى تتآكل ببطء والفقراء يزدادون فقراً. الحلول تتطلب إصلاحات هيكلية جريئة في السياسات الاقتصادية ودعم الإنتاج المحلي وتوفير فرص عمل حقيقية للشباب. #الاقتصاد #التضخم #غلاء_المعيشة"
    },

    # ═══════════════════════════════════════════
    #  THÈME 7 : ÉDUCATION
    # ═══════════════════════════════════════════
    {
        'id': 31,
        'language': 'fr',
        'category': 'education',
        'text': "Le niveau scolaire qui baisse, les enseignants qui démissionnent, les classes surchargées — l'école publique française est en crise et personne ne semble avoir de vraie solution. On forme des enfants pour des métiers qui n'existent pas encore avec des méthodes conçues au XIXe siècle. Il faut repenser entièrement le système éducatif : moins de mémorisation, plus de pensée critique, de créativité et de compétences numériques. Et surtout revaloriser massivement le métier d'enseignant. #Education #EcolePublique #Enseignement"
    },
    {
        'id': 32,
        'language': 'en',
        'category': 'education',
        'text': "Student loan debt in America has crossed 1.7 trillion dollars and it's destroying an entire generation's financial future. Young people are delaying homeownership, marriage and having children because they're drowning in debt for degrees that sometimes don't even lead to good jobs. The system is broken by design — universities raise tuition because loans are available and students borrow because they have no choice. We need free community college at minimum. #StudentDebt #HigherEducation #CollegeAffordability"
    },
    {
        'id': 33,
        'language': 'es',
        'category': 'education',
        'text': "El sistema educativo español necesita una revolución urgente. Seguimos enseñando de la misma manera que hace cincuenta años mientras el mundo ha cambiado radicalmente. Los estudiantes memorizan contenidos que pueden encontrar en Google en dos segundos en lugar de aprender a pensar, crear y colaborar. Los docentes están infravalorados y mal pagados para la importancia crucial que tienen. Necesitamos menos burocracia y más autonomía pedagógica. #Educación #Escuela #Docentes #Innovación"
    },
    {
        'id': 34,
        'language': 'de',
        'category': 'education',
        'text': "Das deutsche Bildungssystem erzeugt Ungleichheit statt sie zu überwinden. Welches Gymnasium ein Kind besucht hängt immer noch zu sehr vom Bildungsstand der Eltern ab als von den eigenen Fähigkeiten. Das ist nicht gerecht und es ist auch wirtschaftlich dumm — wir verschwenden enormes Potenzial. Ganztagesschulen, kostenlose Kitas und eine bessere Förderung von Kindern aus bildungsfernen Familien sind der Weg nach vorne. #Bildung #Schule #Chancengleichheit #Deutschland"
    },
    {
        'id': 35,
        'language': 'ar',
        'category': 'education',
        'text': "مناهجنا الدراسية في كثير من الدول العربية لا تزال تُعلم الحفظ والتلقين بدلاً من التفكير النقدي والإبداع والابتكار. الطالب العربي يحفظ كتباً كاملة ثم ينساها بعد الامتحان لأن التعليم لم يكن موصولاً بالتفكير الحقيقي. في عالم تحكمه التقنية والبيانات والذكاء الاصطناعي نحتاج جيلاً يحل المشكلات ويبتكر الحلول. إصلاح التعليم هو أهم استثمار تقوم به أي حكومة عربية اليوم. #التعليم #الإصلاح_التربوي #الشباب #المستقبل"
    },

    # ═══════════════════════════════════════════
    #  THÈME 8 : CULTURE
    # ═══════════════════════════════════════════
    {
        'id': 36,
        'language': 'fr',
        'category': 'culture',
        'text': "Vu le dernier film de Scorsese hier soir et je suis encore sous le choc. Trois heures et demie qui passent comme rien tellement le film est dense, maîtrisé et profond. Le cinéma américain sait encore produire des œuvres qui comptent quand on lui en donne les moyens. Mais je m'inquiète pour l'avenir — les studios préfèrent les franchises Marvel aux films d'auteur. Les plateformes streaming ont sauvé certains projets mais ont aussi uniformisé les contenus vers le bas. #Cinema #Culture #Scorsese #Hollywood"
    },
    {
        'id': 37,
        'language': 'en',
        'category': 'culture',
        'text': "The Beyoncé Renaissance tour was not just a concert — it was a full cultural moment that redefined what live music can be. The production, the choreography, the setlist, the costumes — every single detail was perfect. She doesn't just perform, she creates an immersive experience that makes you feel part of something bigger than yourself. In an era of disposable content and three-second attention spans, she proved that ambitious artistic vision still matters. #Beyonce #Music #Culture #Renaissance"
    },
    {
        'id': 38,
        'language': 'es',
        'category': 'culture',
        'text': "El auge de las series españolas en plataformas internacionales es un fenómeno cultural impresionante. La Casa de Papel, Élite, El tiempo entre costuras — producciones españolas que han conquistado audiencias en ciento cincuenta países. Esto demuestra que el talento creativo en España es enorme y que las historias bien contadas no tienen fronteras lingüísticas ni culturales. Netflix y HBO han invertido fuertemente en producción española y los resultados hablan por sí solos. #SeriesEspañolas #Netflix #CulturaEspañola"
    },
    {
        'id': 39,
        'language': 'de',
        'category': 'culture',
        'text': "Die Frankfurter Buchmesse ist jedes Jahr eine Erinnerung daran warum Bücher und Literatur unverzichtbar für unsere Gesellschaft sind. In einer Welt voller digitaler Reizüberflutung bietet ein gutes Buch etwas was kein Algorithmus ersetzen kann — tiefes Nachdenken, Empathie und das Eintauchen in andere Welten. Die deutsche Verlagsbranche ist kreativ und vielfältig aber sie muss sich digital transformieren um die junge Generation zu erreichen. #Buchmesse #Literatur #Lesen #Kultur"
    },
    {
        'id': 40,
        'language': 'ar',
        'category': 'culture',
        'text': "الموسيقى العربية تمر بمرحلة تحول مثيرة بين الأصالة والمعاصرة. فنانون شباب يمزجون بين الطرب الأصيل والإيقاعات الحديثة والكلمات التي تعبر عن هموم جيلهم وأحلامهم. أم كلثوم وفيروز لا تزال حاضرتين في الوجدان لكن الساحة الآن تتسع لأصوات جديدة من المغرب إلى الخليج. المهرجانات الموسيقية العربية تجمع ملايين المشجعين. الثقافة العربية حية ومتجددة وقادرة على التكيف مع العصر. #الموسيقى_العربية #الثقافة #الفن #التراث"
    },

    # ═══════════════════════════════════════════
    #  THÈME 9 : TECHNOLOGIE / RÉSEAUX SOCIAUX
    # ═══════════════════════════════════════════
    {
        'id': 41,
        'language': 'fr',
        'category': 'technologie',
        'text': "TikTok est en train de détruire la capacité de concentration des jeunes générations et personne n'en parle suffisamment. Des vidéos de 15 secondes en boucle, des algorithmes conçus pour créer l'addiction, des contenus de plus en plus courts et abrutissants. Les études neurologiques sont claires — l'exposition massive aux réseaux sociaux modifie le développement du cerveau adolescent. Il faut une régulation sérieuse de ces plateformes et une vraie éducation aux médias dans les écoles. #TikTok #ReseauxSociaux #Addiction"
    },
    {
        'id': 42,
        'language': 'en',
        'category': 'technologie',
        'text': "Twitter / X under Elon Musk has become a completely different platform and honestly I'm still not sure if that's good or bad. The verification system is chaotic, misinformation spreads faster than ever, and half the accounts I used to follow have left. But the engagement is somehow higher than before and the conversations are rawer and more unfiltered. What's clear is that one billionaire having that much control over global public discourse is a genuine threat to democracy. #Twitter #X #ElonMusk #SocialMedia"
    },
    {
        'id': 43,
        'language': 'es',
        'category': 'technologie',
        'text': "El metaverso que Mark Zuckerberg prometió como el futuro de internet parece haberse convertido en el mayor fracaso tecnológico de la década. Meta ha perdido cientos de miles de millones de dólares en este proyecto y el resultado es un mundo virtual donde no hay casi nadie. La gente simplemente no quiere vivir con gafas de realidad virtual puestas. Sin embargo la realidad aumentada en el mundo físico sí tiene futuro real en educación, medicina y entretenimiento. #Metaverso #Meta #Zuckerberg #RealidadVirtual"
    },
    {
        'id': 44,
        'language': 'de',
        'category': 'technologie',
        'text': "Die Einführung von 5G in Deutschland geht viel zu langsam voran. Während Südkorea und China bereits flächendeckend mit 5G versorgt sind kämpfen wir noch mit Funklöchern auf dem Land. Schnelles Internet ist keine Luxus sondern eine Grundinfrastruktur wie Strom und Wasser — ohne sie können sich ländliche Regionen wirtschaftlich nicht entwickeln und digitale Bildung bleibt Theorie. Die Digitalisierung Deutschlands muss endlich Fahrt aufnehmen. #5G #Digitalisierung #Internet #Deutschland"
    },
    {
        'id': 45,
        'language': 'ar',
        'category': 'technologie',
        'text': "منصات التواصل الاجتماعي باتت سلاحاً ذا حدين في العالم العربي. من جهة فتحت أمام الشباب العربي نافذة على العالم وأتاحت لهم التعبير عن آرائهم ونشر إبداعاتهم وبناء مجتمعات افتراضية عابرة للحدود. ومن جهة أخرى أصبحت ساحة للتضليل الإعلامي ونشر الكراهية وتعميق الانقسامات. نحتاج إلى ثقافة رقمية حقيقية تعلم المستخدم كيف يميز بين المعلومة الموثوقة والمزيفة. #التواصل_الاجتماعي #الإعلام_الرقمي #الشباب_العربي"
    },
]


def get_corpus():
    """Retourne le corpus complet"""
    return CORPUS


def get_corpus_by_language(language):
    """Retourne les textes d'une langue spécifique"""
    return [item for item in CORPUS if item['language'] == language]


def get_corpus_by_category(category):
    """Retourne les textes d'une catégorie spécifique"""
    return [item for item in CORPUS if item['category'] == category]


def get_corpus_statistics():
    """Retourne des statistiques sur le corpus"""
    languages = {}
    categories = {}

    for item in CORPUS:
        lang = item['language']
        cat = item['category']

        languages[lang] = languages.get(lang, 0) + 1
        categories[cat] = categories.get(cat, 0) + 1

    return {
        'total_texts': len(CORPUS),
        'languages': languages,
        'categories': categories
    }


if __name__ == "__main__":
    stats = get_corpus_statistics()
    print("Statistiques du corpus:")
    print(f"  Nombre total de textes : {stats['total_texts']}")
    print(f"  Langues                : {stats['languages']}")
    print(f"  Catégories             : {stats['categories']}")

    lengths = [len(item['text']) for item in CORPUS]
    print(f"  Longueur moyenne       : {sum(lengths)//len(lengths)} caractères")
    print(f"  Texte le plus court    : {min(lengths)} caractères")
    print(f"  Texte le plus long     : {max(lengths)} caractères")