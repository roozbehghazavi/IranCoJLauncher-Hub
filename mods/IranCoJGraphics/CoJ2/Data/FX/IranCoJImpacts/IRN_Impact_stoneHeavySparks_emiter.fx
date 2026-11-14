EmiterDef()
{
	LifeTime()
	{
		keyf(0, 0.35)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 9)
	}

	StartVelocity()
	{
		keyf(0, 850)
	}

	StartVelocityRand()
	{
		keyv(0, 420, 300, 420)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")
}
