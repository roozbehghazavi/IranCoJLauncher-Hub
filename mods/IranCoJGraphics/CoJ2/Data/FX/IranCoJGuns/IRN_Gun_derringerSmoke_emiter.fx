EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 0.8)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 3)
	}

	StartVelocity()
	{
		keyf(0, 650)
	}

	StartVelocityRand()
	{
		keyv(0, 97.5, 195, 195)
	}

	Direction()
	{
		keyv(0, -1, 0, 0)
	}

	GenArea("point")
}
