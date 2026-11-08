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
		keyf(0.000000, 9.000000)
	}

	StartVelocity()
	{
		keyf(0.000000, 120.000000)
	}

	StartVelocityRand()
	{
		keyv(0.000000, 120.000000, 120.000000, 120.000000)
	}

	Position()
	{
		keyv(0.000000, 0.000000, 0.000000, 0.000000)
	}

	Direction()
	{
		keyv(0.000000, 0.000000, 1.000000, 0.000000)
	}
	
	AlphaFadeIn("worst", 30, 50)
	AlphaFadeIn("best", 30, 50)

}

