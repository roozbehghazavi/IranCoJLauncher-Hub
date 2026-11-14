EmiterDef()
{
	LifeTime()
	{
		keyf(0, 0.45)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 3)
	}

	StartVelocity()
	{
		keyf(0, 160)
	}

	StartVelocityRand()
	{
		keyv(0, 120, 120, 120)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")
}
