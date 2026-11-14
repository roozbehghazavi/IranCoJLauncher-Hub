EmiterDef()
{
	LifeTime()
	{
		keyf(0, 0.9)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 4)
	}

	StartVelocity()
	{
		keyf(0, 180)
	}

	StartVelocityRand()
	{
		keyv(0, 110, 60, 110)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")
}
