EmiterDef()
{
	LifeTime()
	{
		keyf(0, 2.2)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 1)
	}

	StartVelocity()
	{
		keyf(0, 260)
	}

	StartVelocityRand()
	{
		keyv(0, 0, 90, 0)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
