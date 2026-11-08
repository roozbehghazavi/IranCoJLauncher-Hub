EmiterDef()
{
	Space("world")

	GenType("one_time")

	GenArea("point")

	LifeTime()
	{
		keyf(0.000000, 1.000000)
	}

	NumParticles()
	{
		keyf(0.000000, 17.000000)
	}

	StartVelocity()
	{
		keyf(0.000000, 160.000000)
	}

	StartVelocityRand()
	{
		keyv(0.000000, 110.000000, 111.000000, 110.000000)
	}

	Direction()
	{
		keyv(0.000000, 0.000000, 1.000000, 0.000000)
	}

	AlphaFadeIn("worst", 50, 50)
	AlphaFadeIn("best", 50, 50)
}

